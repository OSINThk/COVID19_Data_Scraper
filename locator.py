from googlemaps import Client as GoogleMaps
import requests
from bs4 import BeautifulSoup as soup


class Coordinates:
    lat = ""
    long = ""

def get_coodinates(country,city):
    gmaps = GoogleMaps('')
    try:
        geocode_result = gmaps.geocode(city +","+country)
        coordinates = Coordinates()
        coordinates.lat = geocode_result[0]['geometry']['location']['lat']
        coordinates.long = geocode_result[0]['geometry']['location']['lng']
        return coordinates
    except:
        return 0


def get_geojson_polygon_coordinates(country,city):
    if city == "":
        http = requests.get(
            "https://nominatim.openstreetmap.org/search.php?q=" + country + "&polygon_geojson=1&format=geojson")
    else:
        http = requests.get(
            "https://nominatim.openstreetmap.org/search.php?q=" + city + "+" + country + "&polygon_geojson=1&format=geojson")
    if http.status_code == 200:
        if is_geojson_valid(http.json()):
            return (parse_geojson(http.json()))
        else:
            return False



def is_geojson_valid(geojson):
    for t in geojson['features']:
        if t != "":
            return True
        else:
            return False

def update_geojson(geojson,country,city,total,current,dead):
    for t in geojson['features']:
        t["properties"] = {
            "Country" : country,
            "City" : city,
            "Total cases": total,
            "Current cases": current,
            "Deceased": dead
        }
    return geojson


def get_city_name(geojson):
    for t in geojson['features']:
        return t["properties"]["City"]

def get_country_name(geojson):
    for t in geojson['features']:
        return t["properties"]["Country"]

def parse_geojson(geojson):
    for t in geojson['features']:
        t["properties"] = {
            "Country" : "",
            "City" : "",
            "Total cases" : 0,
            "Current cases": 0,
            "Deceased" : 0
        }
    return geojson
