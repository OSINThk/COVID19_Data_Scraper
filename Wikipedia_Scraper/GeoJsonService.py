import csv
import os

from geojson import Point, Feature, FeatureCollection, dump
from geopy import Nominatim

from utils import sanitize_text, sanitize_digit


class GeoJsonService(object):
    def __init__(self, geocoding_db_file="geocoding-db.csv"):
        self.geocoding_db = {}
        self.geocoding_db_file = geocoding_db_file
        self.polygon_url = f"https://nominatim.openstreetmap.org/search.php?"
        self.load_geocoding_db()

    def load_geocoding_db(self):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        if '/var/task' in parent_dir_path:
            parent_dir_path = os.getcwd()
        filepath = os.path.join(parent_dir_path, self.geocoding_db_file)
        with open(filepath, encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                country = row["country"]
                region = row["region"]
                lat = row["lat"]
                long = row["long"]
                self.geocoding_db[(country, region)] = (lat, long)

    def produce_geojson_for_rows(self, rows, output_file="covid_data_v2.geojson"):
        features = []
        for row in rows:
            try:
                row_feature = self.get_features_for_row(row.get("country",""), row.get("region",""), row.get("infected",""),
                                                        row.get("deaths",""), row.get("recoveries",""), row.get("long",""),
                                                        row.get("lat",""), row.get("last_updated",""),row.get("active",""),
                                                        row.get("total_per_mil",""), row.get('deaths_per_mil',""),
                                                        row.get('total_tests',""))
                if row_feature:
                    features.append(row_feature)
            except Exception as e:
                print(e, row)
        feature_collection = FeatureCollection(features)
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        if '/var/task' in parent_dir_path:
            parent_dir_path = os.getcwd()
        filepath = os.path.join(parent_dir_path, output_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            dump(feature_collection, f)

    def get_features_for_row(self, country, region, infected, deaths, recoveries, long, lat, last_updated, active="", total_per_mil="", deaths_per_mil="", total_tests=""):
        if active:
            current = str(active)
        else:
            try:
                current = int(infected) - int(deaths) - int(recoveries)
                current = str(current)
            except Exception as e:
                current = ""
        if lat == "" or long == "":
            lat, long = self.get_lat_long(country, region)
        if not lat:
            return
        point = Point((float(long), float(lat)))
        data_type = "Regional" if region else "National"
        feature = Feature(geometry=point,
                          properties={
                              "Data Type": data_type, "Country": sanitize_text(country), "City": sanitize_text(region), "Current Cases": sanitize_digit(current),
                              "Total Cases": sanitize_digit(infected), "Deceased": sanitize_digit(deaths), "Recovered": sanitize_digit(recoveries),
                              "Total Cases/1M pop": sanitize_digit(total_per_mil), "Deaths/1M pop": sanitize_digit(deaths_per_mil),
                              "Total Tests": sanitize_digit(total_tests), "Last Updated": last_updated
                          })
        return feature

    def get_lat_long(self, country, region):
        if (country, region) in self.geocoding_db:
            return self.geocoding_db[(country, region)]
        try:
            print(f"{(country, region)} not present in DB. Fetching coordinates.")
            if region == "":
                q = f"{country}"
            else:
                q = f"{region}, {country}"

            geolocator = Nominatim(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/80.0.3987.149 Safari/537.36")
            location = geolocator.geocode(q, timeout=100)
            lat, long = location.latitude, location.longitude
            self.save_to_geocoding_db(country, region, lat, long)
            return lat, long
        except Exception as e:
            print(f"Exception processing {country}, {region}: {e}")
            self.save_to_geocoding_db(country, region, "", "")
            return "", ""

    def save_to_geocoding_db(self, country, region, lat, long):
        self.geocoding_db[(country, region)] = (lat, long)
        record = dict(country=country,
                      region=region,
                      lat=lat,
                      long=long)
        fields = record.keys()
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        if '/var/task' in parent_dir_path:
            parent_dir_path = os.getcwd()
        filepath = os.path.join(parent_dir_path, self.geocoding_db_file)
        mode = 'a' if os.path.exists(filepath) else "w"
        with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
            if mode == "w":
                writer.writeheader()
            writer.writerow(record)
