import csv
import os
import re

from WikipediaService import WikipediaService
from GeoJsonService import GeoJsonService
import datetime


class MainProgram(object):
    def __init__(self, input_file, output_file="output.csv", geojson_input_file=None):
        if geojson_input_file is None:
            geojson_input_file = output_file
        self.input_file = input_file
        self.output_file = output_file
        self.geojson_file = geojson_input_file
        self.geojson_service = GeoJsonService()
        self.global_stats = None
        self.last_updated = datetime.datetime.now()

    def cleanup(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.output_file)
        if os.path.exists(filepath):
            os.remove(filepath)

    def run(self):
        self.cleanup()
        self.process_input_file()
        self.produce_geojson_for_file()

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

    def process_input_file(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.input_file)
        with open(filepath, encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            self.process_input(csv_reader)

    def write_record_to_output(self, record):
        fields = record.keys()
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, self.output_file)
        mode = 'a' if os.path.exists(filepath) else "w"
        with open(filepath, mode, newline='') as csvfile:
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
            if not res:
                res = ["No Data", "0", "0", "0"]
            rec = [res]
        self.write_output_for_country(country, rec)

    def write_output_for_country(self, country, output):
        for row in output:
            record = dict(country=self.sanitize_text(country),
                          region=self.sanitize_text(row[0]),
                          infected=self.sanitize_digit(row[1]),
                          deaths=self.sanitize_digit(row[2]),
                          recoveries=self.sanitize_digit(row[3]),
                          last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            self.write_record_to_output(record)

    def produce_geojson_for_file(self, input_file=None):
        if input_file is None:
            input_file = self.geojson_file
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, input_file)
        with open(filepath, encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                self.produce_geojson(row["country"], row["region"], row["infected"], row["deaths"], row["recoveries"])

    def produce_geojson_for_file(self, input_file=None):
        if input_file is None:
            input_file = self.geojson_file
        self.geojson_service.produce_geojson(input_file)

    def produce_geojson(self, country, region, infected, deaths, recoveries):
        print(country, region, infected, deaths, recoveries)
        geojson = self.geojson_service.get_geojson_polygon_coordinates(country, region)
        if geojson:
            geojson = self.geojson_service.update_geojson(geojson, country, region, infected, deaths, recoveries)
            self.geojson_service.dump_geojson(geojson)

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
    m = MainProgram(input_file="wikipedia_input.csv", output_file="covid_output.csv")
    m.run()
