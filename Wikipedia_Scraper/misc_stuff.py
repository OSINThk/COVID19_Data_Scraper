import datetime
import os

import pandas as pd
import csv
import requests
from io import StringIO

columns = ["country", "region", "infected", "deaths", "recoveries", "long", "lat", "last_updated"]
other_output_csv = "other_data.csv"


def write_record_to_output(record):
    fields = record.keys()
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(parent_dir_path, other_output_csv)
    mode = 'a' if os.path.exists(filepath) else "w"
    with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
        if mode == "w":
            writer.writeheader()
        writer.writerow(record)


def write_to_file(country, region, infected="", deaths="", recoveries="", long="", lat=""):
    record = dict(country=country,
                  region=region,
                  infected=infected,
                  deaths=deaths,
                  recoveries=recoveries,
                  long=long,
                  lat=lat,
                  last_updated=last_updated.strftime("%Y-%m-%d %H:%M:%S"))
    write_record_to_output(record)


def scrape_philipines_data():
    r = requests.get("https://services5.arcgis.com/mnYJ21GiFTR97WFg/arcgis/rest/services/municitycent/FeatureServer/0"
                     "/query?f=json&where=count_%3E%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects"
                     "&outFields=*&orderByFields=count_%20desc&resultOffset=0&resultRecordCount=100&cacheHint=true")
    response = r.json()
    for feature in response["features"]:
        attributes = feature["attributes"]
        city = attributes["ADM3_EN"]
        count = attributes["count_"]
        latitude = attributes["latitude"]
        longitude = attributes["longitude"]
        write_to_file(country="Philippines", region=city, infected=count, long=longitude, lat=latitude)
        print(f'"Philippines","{city}","{latitude}","{longitude}"')


def scrape_china_data():
    r = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                     "/csse_covid_19_daily_reports/04-01-2020.csv")
    req = StringIO(r.text)
    df = pd.read_csv(req)
    china_df = df.loc[df["Country_Region"] == "China"]

    for index, row in china_df.iterrows():
        country = row["Country_Region"]
        region = row["Province_State"]
        confirmed = row["Confirmed"]
        deaths = row["Deaths"]
        recoveries = row["Recovered"]
        active = row["Active"]
        latitude = row["Lat"]
        longitude = row["Long_"]
        write_to_file(country=country, region=region, infected=confirmed, deaths=deaths, recoveries=recoveries,
                      long=longitude, lat=latitude)


def cleanup():
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(parent_dir_path, other_output_csv)
    if os.path.exists(filepath):
        os.remove(filepath)


if __name__ == '__main__':
    last_updated = datetime.datetime.now()
    cleanup()
    scrape_philipines_data()
    scrape_china_data()
