import os
import csv
from geojson import Point, Feature, FeatureCollection, dump
from locator import  get_city_name,get_country_name

def write_to_csv(country,country_data):
    with open(country+'.csv', mode='w') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in country_data:
            spamwriter.writerow([row.name, row.coordinates.long, row.coordinates.lat,row.totalcases,row.current_number, row.deceased])

# Export geojson if with points
def export_geojson(country,country_data):
    features = []
    for row in country_data:
        point = Point((row.coordinates.long, row.coordinates.lat))
        features.append(Feature(geometry=point, properties={"country": country, "city": row.name, "Current Numbers": row.current_number, "Total Cases": row.totalcases, "Deceased Number": row.deceased}))
        feature_collection = FeatureCollection(features)
    with open(country+'.geojson', 'w') as f:
        dump(feature_collection, f)


def dump_geojson(geojson):
    city = get_city_name(geojson)
    country = get_country_name(geojson)
    if not os.path.exists(country):
        os.mkdir(country)
    with open(country+"/"+city+'.geojson', 'w') as f:
        dump(geojson, f)
