# Wikipedia Scraper

## How it works

- You make `wikipedia_input.csv` with countries input wikipedia url and paramaters.
    - If you add a country that doesn't have a wiki page/table details. It will grab the whole country details from [2019–20 coronavirus pandemic](https://en.m.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_pandemic) Wikipedia page's main stats table.
    - If you provide it with table details along with columns, it will grab those details. In case it a column isn't defined it's value is defaulted to 0.
- You run the scraper and see the magic happen. It will create folders with a geojson for each city.
    - In case there were no cities, it will create the geojson file with the name `all.geojson` under the respective Country's folder.
    - It grabs the geojson polygon details from OpenStreetMaps API.

## Running the program
- Install Python 3 and add it to path.
- Update the `wikipedia_input.csv` with countries/wikipedia url and metadata.
- Run `pip install -t requirements.txt` to install required packages.
- Run the program using `python MainProgram.py`