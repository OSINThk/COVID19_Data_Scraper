import csv
import os
import re

from WikipediaService import WikipediaService
from GeoJsonService import GeoJsonService
import datetime


class MainProgram(object):
    def __init__(self, input_file="wikipedia_input.csv", scraper_output_file="scraper_output.csv",
                 static_geojson_csv_file=None,
                 geojson_output_file="covid_data.geojson"):
        self.input_file = input_file
        self.scraper_output_file = scraper_output_file
        self.static_geojson_csv_file = static_geojson_csv_file
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
        self.produce_geojson_for_files()

    def get_global_stats(self, country):
        if not self.global_stats:
            scraper = WikipediaService()
            res = scraper.get_global_stats()
            self.global_stats = res
        for row in self.global_stats:
            if country in row[0]:
                row[0] = ""
                return row
        return None

    def get_total_stats(self):
        if not self.global_stats:
            scraper = WikipediaService()
            res = scraper.get_global_stats()
            self.global_stats = res
        row = self.global_stats[0]
        d = dict(country="Global",
                 infected = self.sanitize_digit(row[1]),
                 deaths = self.sanitize_digit(row[2]),
                 recoveries = self.sanitize_digit(row[3]),
                 last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
        return d

    def process_input_file(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.input_file)
        with open(filepath, encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            self.process_input(csv_reader)

    def write_record_to_output(self, record):
        fields = record.keys()
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.scraper_output_file)
        mode = 'a' if os.path.exists(filepath) else "w"
        with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
            if mode == "w":
                writer.writeheader()
            writer.writerow(record)

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
            except Exception as e:
                print(e)
                res = self.get_global_stats(country)
                if not res:
                    res = ["No Data", "0", "0", "0"]
                rec = [res]
        else:
            res = self.get_global_stats(country)
            print(f"Using global stats for {country}.")
            if not res:
                res = ["No Data", "0", "0", "0"]
            rec = [res]
        self.write_output_for_country(country, rec)

    def write_output_for_country(self, country, output):
        for row in output:
            lat, long = self.geojson_service.get_lat_long(country, self.sanitize_text(row[0]))
            record = dict(country=self.sanitize_text(country),
                          region=self.sanitize_text(row[0]),
                          infected=self.sanitize_digit(row[1]),
                          deaths=self.sanitize_digit(row[2]),
                          recoveries=self.sanitize_digit(row[3]),
                          long=long,
                          lat=lat,
                          last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            self.write_record_to_output(record)

    def produce_geojson_for_files(self, input_files=None):
        if input_files is not None and type(input_files) == list:
            geojson_input_files = input_files
        else:
            geojson_input_files = [self.scraper_output_file]
            if self.static_geojson_csv_file is not None:
                geojson_input_files.append(self.static_geojson_csv_file)
        rows = []
        for file in geojson_input_files:
            print(f"Processing {file}.")
            parent_dir_path = os.path.dirname(os.path.realpath(__file__))
            filepath = os.path.join(parent_dir_path, file)
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
    m = MainProgram(input_file="wikipedia_input.csv", static_geojson_csv_file="static_output.csv",
                    scraper_output_file="scraper_output.csv")
    m.run()
    #m.produce_geojson_for_files()