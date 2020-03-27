import requests
import geojson
import os


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
