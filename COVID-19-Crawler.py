import csv
import bs4
from locator import get_coodinates,Coordinates

from bs4 import BeautifulSoup as soup




class Country:
    values = 0
    sources = []
    def __init__(self,name,coordinates):
        self.name = name
        self.coordinates = coordinates

def get_countries_list():
    Countries_list = []
    with open('countries.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            tmp_location = get_coodinates(row[0])
            tmp_country = Country(row[0], tmp_location)
            Countries_list.append(tmp_country)
    return Countries_list

def load_country_repos(lst_countries):
    with open('db.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            for country_i in lst_countries:
                if row[0] == country_i.name:
                    country_i.sources.append(row[3])










if __name__ == "__main__":
    lst_countries = get_countries_list()
    load_country_repos(lst_countries)







