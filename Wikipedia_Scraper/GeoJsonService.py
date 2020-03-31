import csv

import requests
import geojson
import os

from geojson import Point, Feature, FeatureCollection, dump
from geopy import Nominatim


class GeoJsonService(object):
    def __init__(self):
        self.polygon_url = f"https://nominatim.openstreetmap.org/search.php?"

    def get_geojson_polygon_coordinates(self, country, city):
        if city == "":
            querystring = dict(polygon_geojson="1", format="geojson", q=country)
        else:
            querystring = dict(format="geojson", q=f"{country} {city}")
        http = requests.get(self.polygon_url, params=querystring)
        if http.status_code == 200:
            if self.is_geojson_valid(http.json()):
                return self.parse_geojson(http.json())
            else:
                return False

    @staticmethod
    def is_geojson_valid(geojson):
        for t in geojson['features']:
            if t != "":
                return True
            else:
                return False

    @staticmethod
    def parse_geojson(geojson):
        for t in geojson['features']:
            t["properties"] = {
                "Country": "",
                "City": "",
                "Total cases": 0,
                "Current cases": 0,
                "Recovered": 0,
                "Deceased": 0
            }
        return geojson

    @staticmethod
    def update_geojson(geojson, country, city, total, dead, recovered):
        current = int(total) - int(dead) - int(recovered)
        current = str(current)
        for t in geojson['features']:
            t["properties"] = {
                "Country": country,
                "City": city,
                "Total cases": total,
                "Current cases": current,
                "Recovered": recovered,
                "Deceased": dead
            }
        return geojson

    def dump_geojson(self, geo_json):
        city = self.get_property(geo_json, "City")
        country = self.get_property(geo_json, "Country")
        if not (country):
            return
        if not city:
            city = "all"
        if not os.path.exists(country):
            os.mkdir(country)
        with open(country + "/" + city + '.geojson', 'w') as f:
            geojson.dump(geo_json, f)

    @staticmethod
    def get_property(geo_json, key):
        features = geo_json.get("features")
        if features:
            properties = features[0].get("properties", dict())
            return properties.get(key)
        return ""

    def produce_geojson(self, input_file=None):
        parent_dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(parent_dir_path, input_file)
        features = []
        with open(filepath, encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                try:
                    row_feature = self.get_features_for_row(row["country"], row["region"], row["infected"], row["deaths"],
                                                       row["recoveries"], row["last_updated"])
                except Exception as e:
                    print(e, print(row["country"], row["region"], row["infected"], row["deaths"],
                                   row["recoveries"]))
                features.append(row_feature)
        feature_collection = FeatureCollection(features)
        with open('covid_data.geojson', 'w') as f:
            dump(feature_collection, f)

    def get_features_for_row(self, country, region, infected, deaths, recoveries, last_updated=None):
        print(country, region, infected, deaths, recoveries)
        lat, long = self.get_lat_long(country, region)
        current = int(infected) - int(deaths) - int(recoveries)
        current = str(current)
        point = Point((long, lat))
        feature = Feature(geometry=point,
                          properties={
                              "Country": country, "City": region, "Current Cases": current,
                              "Total Cases": infected, "Deceased": deaths, "Recovered": recoveries,
                              "Last Updated": last_updated
                          })
        return feature

    @staticmethod
    def get_lat_long(country, region):
        if region == "":
            q = f"{country}"
        else:
            q = f"{region}, {country}"

        geolocator = Nominatim(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
        location = geolocator.geocode(q, timeout=100)
        lat, long = location.latitude, location.longitude
        return lat, long

