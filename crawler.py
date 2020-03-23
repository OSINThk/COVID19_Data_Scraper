from bs4 import BeautifulSoup as soup
from locator import get_coodinates
from output_lib import write_to_csv,export_geojson
import requests

class City:
    def __init__(self, name, coordinates,total,curent,dead):
        self.name = name
        self.coordinates = coordinates
        self.totalcases = total
        self.current_number = curent
        self.deceased = dead

def get_wiki_Korea_numbers():
    tmp_data = []
    http = requests.get("https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Korea")
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
                coordinates = get_coodinates(country,city_name)
                if coordinates != 0:
                    tmp_city = City(city_name,coordinates,cols[0],cols[3],cols[5])
                    tmp_data.append(tmp_city)
                else:
                    print("a")
    write_to_csv("Korea",tmp_data)
    export_geojson("Korea",tmp_data)

