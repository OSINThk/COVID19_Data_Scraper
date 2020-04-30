# app.py
from flask import Flask, jsonify
import json
from MainProgram import MainProgram
import time
import os
from flask_cors import cross_origin

app = Flask(__name__)

geojson_new_file = "covid_data_v2.geojson"
json_data_file = "covid_data_v3.json"
global_data_file = "data_national.json"
regional_data_file = "data_regional.json"


@app.route('/v2/data')
@cross_origin()
def get_new_data():
    """
    Returns the data from 'covid_data.geojson' file.
    :return: 'covid_data.geojson' file
    """
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    filepath = os.path.join(parent_dir_path, geojson_new_file)
    with open(filepath) as geojson_data:
        data = json.load(geojson_data)
    return jsonify(data)


@app.route('/v3/data/national')
@cross_origin()
def get_national_data():
    """
    Returns the national data from 'covid_data.geojson' file.
    :return: 'covid_data.json' file
    """
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    filepath = os.path.join(parent_dir_path, global_data_file)
    with open(filepath) as geojson_data:
        data = json.load(geojson_data)
    return jsonify(data)


@app.route('/v3/data/regional')
@cross_origin()
def get_regional_data():
    """
    Returns the regional data from 'covid_data.geojson' file.
    :return: 'covid_data.json' file
    """
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    if '/var/task' in parent_dir_path:
        parent_dir_path = os.getcwd()
    filepath = os.path.join(parent_dir_path, regional_data_file)
    with open(filepath) as geojson_data:
        data = json.load(geojson_data)
    return jsonify(data)


@app.route('/global', methods=['GET'])
def global_total():
    m = MainProgram(input_file="wikipedia_input.csv", scraper_output_file="wikipedia_output.csv")
    global_data = m.get_total_stats()
    return jsonify(global_data)


@app.route('/update_data', methods=['GET'])
def run_scraper():
    """
    Runs the scraper to create 'scraper_output.csv' file and then
    uses this and 'static_output.csv' to create 'covid_data.geojson' file.
    :return: Response
    """
    start = time.time()
    m = MainProgram(input_file="wikipedia_input.csv", scraper_output_file="wikipedia_output.csv")
    m.run()
    end = time.time()
    elapsed_seconds = round(end - start, 2)
    return jsonify({"Message": f"Successfully completed scraping! Took {elapsed_seconds}s to update!"})


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)