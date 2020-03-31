# app.py
from flask import Flask, jsonify
import json
from MainProgram import MainProgram
import time
import os

app = Flask(__name__)

geojson_file = "covid_data.geojson"


@app.route('/data', methods=['GET'])
def get_data():
    """
    Returns the data from 'covid_data.geojson' file.
    :return: 'covid_data.geojson' file
    """
    data = {}
    parent_dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(parent_dir_path, geojson_file)
    with open(filepath) as geojson_data:
        data = json.load(geojson_data)
    return jsonify(data)


@app.route('/run', methods=['GET'])
def run_scraper():
    """
    Runs the scraper to create 'covid_output.csv' file and updates 'covid_data.geojson' file.
    :return: Response
    """
    start = time.time()
    m = MainProgram(input_file="wikipedia_input.csv", output_file="covid_output.csv")
    m.run()
    end = time.time()
    elapsed_seconds = round(end - start, 2)
    return jsonify({"Message": f"Successfully completed scraping! Took {elapsed_seconds}s to update!"})


@app.route('/update', methods=['GET'])
def update_data():
    """
    Only updates 'covid_data.geojson' file from existing 'covid_output.csv' file.
    :return: Response
    """
    start = time.time()
    m = MainProgram(input_file="wikipedia_input.csv", output_file="covid_output.csv")
    m.produce_geojson_for_file()
    end = time.time()
    elapsed_seconds = round(end - start, 2)
    return jsonify({"Message": f"Successfully updated data! Took {elapsed_seconds}s to update!"})


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
