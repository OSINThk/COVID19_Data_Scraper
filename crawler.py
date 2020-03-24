from bs4 import BeautifulSoup as soup
from locator import get_coodinates, get_geojson_polygon_coordinates, update_geojson
from output_lib import write_to_csv,export_geojson,dump_geojson
import requests

class City:
    def __init__(self, name, geojson):
        self.name = name
        self.geojson = geojson

def get_wiki_Korea_numbers():
    tmp_data = []
    http = requests.get("https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Korea")
    if http.status_code == 200:
        page_soup = soup(http.text, "html.parser")
        country = "south korea"
        table = page_soup.find('table', attrs={'class': 'wikitable float sortable'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        data = []
        for row in rows:
            city_name = row.find('th')
            if city_name:
                city_name = city_name.text.split()
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                if cols:
                    seperator = ' '
                    city_name = seperator.join(city_name)
                    geojson = get_geojson_polygon_coordinates(country,city_name)
                    if geojson != False:
                        geojson = update_geojson(geojson,country,city_name,cols[0],cols[3],cols[5])
                        dump_geojson(geojson)

