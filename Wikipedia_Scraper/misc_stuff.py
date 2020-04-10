import datetime
import json
import os
import time
import pendulum
import pandas as pd
import csv
import requests
from io import StringIO
import numpy as np

from GeoJsonService import GeoJsonService

columns = ["country", "region", "infected", "deaths", "recoveries", "long", "lat", "last_updated"]
hopkins_csv = "output/john_hopkins_output.csv"
taiwan_csv = "output/taiwan.csv"
japan_csv = "output/japan.csv"


def write_record_to_output(record, filename=None):
    if filename is None:
        filename = hopkins_csv
    fields = record.keys()
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(parent_dir_path, filename)
    mode = 'a' if os.path.exists(filepath) else "w"
    with open(filepath, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
        if mode == "w":
            writer.writeheader()
        writer.writerow(record)


def write_to_file(country, region, infected="", deaths="", recoveries="", long="", lat="", filename=None):
    record = dict(country=country,
                  region=region,
                  infected=infected,
                  deaths=deaths,
                  recoveries=recoveries,
                  long=long,
                  lat=lat,
                  last_updated=last_updated.strftime("%Y-%m-%d %H:%M:%S"))
    write_record_to_output(record, filename)


def scrape_china_geojson(file_name):
    from googletrans import Translator
    translator = Translator()
    with open(file_name) as fin, open('output/china.csv', 'w') as fout:
        fout.write('"Country","Address","Address_Translated","Total","Recovered","Deaths","Lat","Long"\n')
        json_dict = json.load(fin)
        for feature in json_dict["features"]:
            while True:
                try:
                    properties = feature["properties"]
                    geometry = feature["geometry"]
                    lat, long = geometry["coordinates"]
                    address = properties["Address"]
                    translation = translator.translate(address)
                    address_translated = translation.text
                    total = properties["cities__confirmedCount"]
                    recovered = ""
                    deaths = ""
                    fout.write(
                        f'"China","{address}","{address_translated}","{total}","{recovered}","{deaths}","{lat}","{long}"\n')
                    print(address, address_translated, total, recovered, deaths, lat, long, sep="\t", end="\n")
                    break
                except Exception as e:
                    print(e, "Retrying in 30 seconds.")
                    time.sleep(30)


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


def scrape_taiwan_data():
    country = "Taiwan"
    g = GeoJsonService()
    r = requests.get("https://services7.arcgis.com/HYXUMO0l0lNCIifa/arcgis/rest/services"
                     "/Wuhan_Coronavirus_Taiwan_County/FeatureServer/0/query?f=json&where=Confirmed%3E0"
                     "&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed"
                     "%20desc&resultOffset=0&resultRecordCount=25&cacheHint=true")
    response = r.json()
    cleanup(taiwan_csv)
    for feature in response["features"]:
        attributes = feature["attributes"]
        city = attributes["COUNTYENG"]
        infected = attributes["Confirmed"]
        recovered = attributes["recover"]
        deaths = attributes["death"]
        latitude, longitude = g.get_lat_long(country, city)
        write_to_file(country=country, region=city, infected=infected, recoveries=recovered, deaths=deaths,
                      long=longitude, lat=latitude, filename=taiwan_csv)


def scrape_china_data(date_str=None):
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%d-%m-%Y")
        print(date_str)
    r = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                     f"/csse_covid_19_daily_reports/{date_str}.csv")
    if r.status_code == 200:
        req = StringIO(r.text)
        df = pd.read_csv(req)
        china_df = df.loc[df["Country_Region"] == "China"]
    else:
        print(r)
        return

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


def scrape_japan_data():
    country = "Japan"
    g = GeoJsonService()
    r = requests.get('https://data.covid19japan.com/summary/latest.json')
    response = r.json()
    prefectures = response["prefectures"]
    cleanup(japan_csv)
    for prefecture in prefectures:
        region = prefecture["name"]
        confirmed = prefecture["confirmed"]
        deaths = prefecture["deaths"]
        recoveries = prefecture["recovered"]
        latitude, longitude = g.get_lat_long(country, region)
        write_to_file(country=country, region=region, infected=confirmed, deaths=deaths, recoveries=recoveries,
                      long=longitude, lat=latitude, filename=japan_csv)


def scrape_world_data(date_str=None):
    excluded_countries = ["China"]
    countries = ["Australia", "Canada", "China", "US"]
    curr_date = pendulum.now()
    processed = False
    if not date_str:
        date_str = curr_date.strftime("%m-%d-%Y")
    while not processed:
        print(date_str)
        print(f"Trying {date_str}...")
        r = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                         f"/csse_covid_19_daily_reports/{date_str}.csv")
        if r.status_code == 200:
            processed = True
        else:
            print(f"Error! Status Code: {r.status_code}")
            curr_date = curr_date.subtract(days=1)
            date_str = curr_date.strftime("%m-%d-%Y")

    if r.status_code == 200:
        req = StringIO(r.text)
        df = pd.read_csv(req).replace(np.nan, '', regex=True)
        df = df[df["Country_Region"].isin(countries)]
    else:
        print(r)
        return
    cleanup(hopkins_csv)
    for index, row in df.iterrows():
        country = row["Country_Region"]
        if country in excluded_countries:
            continue
        city = row["Admin2"]
        region = row["Province_State"] if not city else f'{city}, {row["Province_State"]}'
        confirmed = row["Confirmed"]
        deaths = row["Deaths"]
        recoveries = row["Recovered"]
        active = row["Active"]
        latitude = row["Lat"]
        longitude = row["Long_"]
        if "Unassigned" in region:
            continue
        write_to_file(country=country, region=region, infected=confirmed, deaths=deaths, recoveries=recoveries,
                      long=longitude, lat=latitude, filename=hopkins_csv)
    return df


def calculate_sum_and_write(df):
    total_countries = ["Australia", "Canada", "China", "US"]
    g = GeoJsonService()
    for country in total_countries:
        tmp_df = df.loc[df["Country_Region"] == country]
        row = tmp_df.sum()
        region = ""
        confirmed = row["Confirmed"]
        deaths = row["Deaths"]
        recoveries = row["Recovered"]
        active = row["Active"]
        latitude, longitude = g.get_lat_long(country, region)
        record = dict(country=country,
                      region=region,
                      infected=confirmed,
                      deaths=deaths,
                      recoveries=recoveries,
                      long=longitude,
                      lat=latitude)
        print(record)
        write_to_file(country=country, region=region, infected=confirmed, deaths=deaths, recoveries=recoveries,
                      long=longitude, lat=latitude)


def cleanup(filename=hopkins_csv):
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(parent_dir_path, filename)
    if os.path.exists(filepath):
        os.remove(filepath)


if __name__ == '__main__':
    last_updated = datetime.datetime.now()
    world_df = scrape_world_data()
    scrape_japan_data()
    scrape_taiwan_data()
