from bs4 import BeautifulSoup as soup
from locator import get_coodinates
from csv_handler import write_to_csv
import requests

class City:
    def __init__(self, name, coordinates,values):
        self.name = name
        self.coordinates = coordinates
        self.cases = values

def get_wiki_Korea_numbers():
    tmp_data = []
    http = requests.get("https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Korea")
    page_soup = soup(http.text, "html.parser")
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
            coordinates = get_coodinates(city_name)
            if coordinates != 0:
                tmp_city = City(city_name,coordinates,cols[0])
                tmp_data.append(tmp_city)
    write_to_csv("Korea",tmp_data)

