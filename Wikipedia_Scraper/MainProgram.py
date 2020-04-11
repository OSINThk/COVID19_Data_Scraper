import csv
import os
import re

from WikipediaService import WikipediaService
from GeoJsonService import GeoJsonService
import datetime

from WorldoMeterService import WorldoMeterService


class MainProgram(object):
    def __init__(self, input_file="wikipedia_input.csv", scraper_output_file="scraper_output.csv",
                 geojson_output_file="covid_data.geojson"):
        self.input_file = input_file
        self.scraper_output_file = scraper_output_file
        self.geojson_output_file = geojson_output_file
        self.geojson_service = GeoJsonService()
        self.global_stats = None
        self.last_updated = datetime.datetime.now()

    def cleanup(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.scraper_output_file)
        if os.path.exists(filepath):
            os.remove(filepath)

    def run(self):
        self.cleanup()
        self.process_input_file()
        self.write_global_stats()
        self.process_data_for_thailand()
        self.process_data_for_malaysia()
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

    def write_global_stats(self):
        wms = WorldoMeterService()
        records = wms.get_global_stats()
        self.global_stats = records
        self.write_records_to_file(records, "output/global.csv")

    def get_total_stats(self):

        if not self.global_stats:
            self.write_global_stats()
        row = self.global_stats[0]
        d = dict(country="Global",
                 infected=row["infected"],
                 deaths=row["deaths"],
                 recoveries=row["recoveries"],
                 active=row["active"],
                 last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
        return d

    def process_input_file(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.input_file)
        with open(filepath, encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            self.process_input(csv_reader)

    def write_record_to_output(self, record, file_name=None):
        if file_name is None:
            file_name = self.scraper_output_file
        fields = record.keys()
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, file_name)
        mode = 'a' if os.path.exists(filepath) else "w"
        with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
            if mode == "w":
                writer.writeheader()
            writer.writerow(record)

    def write_records_to_file(self, records, file_name):
        os.remove(file_name)
        for record in records:
            self.write_record_to_output(record, file_name)

    def process_input(self, data):
        for row in data:
            self.process_row(row)

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
                self.write_output_for_country(country, rec)
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
        self.write_output_for_country(country, res)

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
        self.write_output_for_country(country, res)

    def write_output_for_country(self, country, output):
        for row in output:
            region = self.sanitize_text(row.get("region", ""))
            lat, long = self.geojson_service.get_lat_long(country, region)
            record = dict(country=self.sanitize_text(country),
                          region=region,
                          infected=self.sanitize_digit(row.get("infected", "")),
                          deaths=self.sanitize_digit(row.get("deaths", "")),
                          recoveries=self.sanitize_digit(row.get("recoveries", "")),
                          active=self.sanitize_digit(row.get("active", "")),
                          total_per_mil=self.sanitize_digit(row.get("total_per_mil", "")),
                          deaths_per_mil=self.sanitize_digit(row.get("deaths_per_mil", "")),
                          total_tests=self.sanitize_digit(row.get("total_tests", "")),
                          long=long,
                          lat=lat,
                          last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            self.write_record_to_output(record)

    def produce_geojson_for_files(self, input_files=None):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(parent_dir_path, "output")
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
        self.geojson_service.produce_geojson_for_rows(rows)

    @staticmethod
    def sanitize_text(d):
        RE = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
            \[\[[^|^\]]+\||
            \[\[|
            \]\]|
            \'{2,5}|
            (<s>|<!--)[\s\S]+(</s>|-->)|
            {{[\s\S\n]+?}}|
            <ref>[\s\S]+</ref>|
            ={1,6}""", re.VERBOSE)
        x = RE.sub('', d)
        while '[' in x:
            startidx = x.index('[')
            endidx = x.rindex(']')
            x = x[:startidx] + x[endidx + 1:]
        x = x.replace('†', "").strip()
        return x

    @staticmethod
    def sanitize_digit(d):
        x = ''.join(c for c in d if c.isdigit())
        if x:
            return int(x)
        else:
            return 0


if __name__ == "__main__":
    m = MainProgram(input_file="wikipedia_input.csv", scraper_output_file="output/scraper_output.csv")
    m.run()
    # m.produce_geojson_for_files()
