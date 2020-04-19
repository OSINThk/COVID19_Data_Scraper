import csv
import os
import re

from MiscScrapers import MiscScrapers
from WikipediaService import WikipediaService
from GeoJsonService import GeoJsonService
from aws_lib import upload_file_to_s3
from utils import sanitize_digit, sanitize_text, cleanup, write_record_to_output, move_to_final
import datetime

from WorldoMeterService import WorldoMeterService


class MainProgram(object):
    def __init__(self, input_file="wikipedia_input.csv", scraper_output_file="scraper_output.csv",
                 geojson_output_file="covid_data_new_data.geojson"):
        self.input_file = input_file
        self.scraper_output_file = scraper_output_file
        self.geojson_output_file = geojson_output_file
        self.geojson_service = GeoJsonService()
        self.misc_scrapers = MiscScrapers()
        self.global_stats = None
        self.last_updated = datetime.datetime.now()
        self.output_file_names = {
            "malaysia": "malaysia.csv",
            "thailand": "thailand.csv",
            "global": "global.csv",
            "wikipedia": scraper_output_file,
            "default": scraper_output_file
        }

    def get_output_file(self, country=None):
        if country is None:
            country = "default"
        file_name_str = self.output_file_names.get(country.lower(), "")
        if not file_name_str:
            file_name_str = self.output_file_names.get("default")
        if not file_name_str.startswith("output/"):
            file_name = os.path.join("output", file_name_str)
        else:
            file_name = file_name_str
        return file_name

    def run(self):
        self.process_wikipedia_input()
        self.process_global_stats()
        self.process_data_for_thailand()
        self.process_data_for_malaysia()
        self.process_other_countries()
        self.produce_geojson_for_files()

    def get_global_stats(self, country):
        if not self.global_stats:
            scraper = WikipediaService()
            res = scraper.get_global_stats()
            self.global_stats = res
        for row in self.global_stats:
            if country in row["region"]:
                row[0] = ""
                return row
        return None

    def process_other_countries(self):
        self.misc_scrapers.scrape_john_hopkins_data()
        self.misc_scrapers.scrape_japan_data()
        self.misc_scrapers.scrape_taiwan_data()

    def process_global_stats(self):
        wms = WorldoMeterService()
        country = "global"
        records = wms.get_global_stats()
        file_name = self.get_output_file(country)
        cleanup(file_name)
        self.global_stats = records
        self.write_output_for_country(records, file_name=file_name)
        move_to_final(file_name)

    def get_total_stats(self):
        if not self.global_stats:
            self.process_global_stats()
        row = self.global_stats[0]
        d = dict(country="Global",
                 infected=row["infected"],
                 deaths=row["deaths"],
                 recoveries=row["recoveries"],
                 active=row["active"],
                 last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
        return d

    def process_wikipedia_input(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.input_file)
        with open(filepath, encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            self.process_input(csv_reader)

    def process_input(self, data):
        cleanup(self.get_output_file("wikipedia"))
        for row in data:
            self.process_row(row)
        move_to_final(self.get_output_file("wikipedia"))

    def process_row(self, row):
        country = row["Country"]
        wiki_url = row["Wikipedia Page"]
        table_text = row["Table Text"]
        table_idx = row["Table index"]
        row_start = row["Data row starting"]
        row_end = row["Data row ending"]
        region = row["Region column"]
        infected = row["Infected column"]
        death = row["Deaths column"]
        recovered = row["Recovered column"]
        if wiki_url != "-" and table_text != "-":
            try:
                print(f"Fetching stats for {country}.")
                scraper = WikipediaService(country=country, url=wiki_url)
                rec = scraper.process_table(table_text, row_start, row_end, region, infected, death, recovered)
                self.write_output_for_country(rec, country=country, file_name=self.get_output_file("wikipedia"))
            except Exception as e:
                print(e)

    def get_city_name(self, *args):
        lst = []
        for arg in args[::-1]:
            if arg not in lst and 'Federal Territories' not in arg:
                clean_arg = re.sub("[\(\[].*?[\)\]]", "", arg).strip()
                lst.append(clean_arg)
        city_name = ', '.join(lst).strip()
        return city_name

    def process_data_for_malaysia(self):
        a = WikipediaService(url="https://en.m.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Malaysia")
        country = "Malaysia"
        table_text = "District/City"
        start_row = "3"
        table = a.search_table(table_text)
        if start_row.isnumeric():
            table = table[int(start_row) - 1:]
        res = []
        for row in table:
            region = self.get_city_name(row[0], row[1])
            if 'Unknown' in region:
                continue
            infected = row[-1]
            d = dict(
                region=region,
                infected=infected,
                deaths="0",
                recoveries="0",
            )
            res.append(d)
        file_name = self.get_output_file(country)
        cleanup(file_name)
        self.write_output_for_country(res, country=country, file_name=file_name)
        move_to_final(file_name)

    def process_data_for_thailand(self):
        a = WikipediaService(url="https://en.m.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Thailand")
        country = "Thailand"
        table_name = "Confirmed COVID-19 cases"
        start_row = "3"
        end_row = "-2"
        region_col = "2"
        infected_col = "3"
        death_col = "11"
        recovered_col = ""
        table_index = "2"
        z = a.process_table(table_name, start_row, end_row, region_col, infected_col, death_col, recovered_col,
                            table_index=table_index)
        res = []
        for rec in z:
            if "Total" not in rec.get("region"):
                res.append(rec)
        file_name = self.get_output_file(country)
        cleanup(file_name)
        self.write_output_for_country(res, country=country, file_name=file_name)
        move_to_final(file_name)

    def write_output_for_country(self, output, country=None, file_name=None):
        if file_name is None:
            file_name = self.get_output_file("default")
        for row in output:
            if country is None:
                country_str = row.get("country", "")
            else:
                country_str = country
            region = sanitize_text(row.get("region", ""))
            lat, long = self.geojson_service.get_lat_long(country_str, region)
            record = dict(country=sanitize_text(country_str),
                          region=region,
                          infected=sanitize_digit(row.get("infected", "")),
                          deaths=sanitize_digit(row.get("deaths", "")),
                          recoveries=sanitize_digit(row.get("recoveries", "")),
                          active=sanitize_digit(row.get("active", "")),
                          total_per_mil=sanitize_digit(row.get("total_per_mil", "")),
                          deaths_per_mil=sanitize_digit(row.get("deaths_per_mil", "")),
                          total_tests=sanitize_digit(row.get("total_tests", "")),
                          long=long,
                          lat=lat,
                          last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            write_record_to_output(record, file_name)

    def produce_geojson_for_files(self, input_files=None):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(parent_dir_path, "final")
        if input_files is not None and type(input_files) == list:
            geojson_input_files = input_files
        else:
            geojson_input_files = os.listdir(output_dir)
        rows = []
        for file in geojson_input_files:
            print(f"Processing {file}.")
            filepath = os.path.join(output_dir, file)
            with open(filepath, encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    rows.append(row)
        print("Creating geojson file.")
        self.geojson_service.produce_geojson_for_rows(rows, output_file="covid_data_v2.geojson")


def lambda_handler(event=None, context=None):
    import time
    start = time.time()
    m = MainProgram(input_file="wikipedia_input.csv", scraper_output_file="wikipedia_output.csv")
    m.run()
    upload_file_to_s3("covid_data_v2.geojson")
    end = time.time()
    elapsed_seconds = round(end - start, 2)
    message = f"Success! Took {elapsed_seconds}s!"
    print(message)
    return dict(message=message)


if __name__ == "__main__":
    m = MainProgram(input_file="wikipedia_input.csv", scraper_output_file="wikipedia_output.csv")
    m.run()