from Scraper import Scraper
import datetime
from collections import OrderedDict

class WorldoMeterService(object):
    def __init__(self):
        self.url = "https://www.worldometers.info/coronavirus/#countries"
        self.scraper = Scraper(url=self.url)
        self.last_updated = datetime.datetime.now()

    def get_global_stats(self):
        print(f"Fetching global stats.")
        self.scraper = Scraper(
            url="https://www.worldometers.info/coronavirus/#countries")
        table = self.search_table_by_id('main_table_countries_today')
        res = self.process_table(table, "9", "-8", "1", "2", "4", "6", "7", "9", "10", "11")
        return res

    def search_table(self, text, index=0):
        table = self.scraper.find_table_with_text(text, index)
        lst = self.scraper.table_to_2d_list(table)
        return lst

    def search_table_by_id(self, table_id):
        table = self.scraper.find_table_by_id(table_id)
        lst = self.scraper.table_to_2d_list(table)
        return lst

    def process_table(self, table, start_row, end_row, country_col, total_col, death_col, recovered_col,
                      active_col, total_per_mil_col, deaths_per_mil_col, total_tests_col):
        if start_row.isnumeric():
            table = table[int(start_row) - 1:]
        if end_row.lstrip('-+').isnumeric():
            table = table[:int(end_row)]
        result = []
        region = ""
        for row in table:
            country = row[int(country_col) - 1]
            total = deceased = recovered = active = total_per_mil = total_tests = deaths_per_mil = "0"
            if total_col.isnumeric():
                total = row[int(total_col) - 1]
                total = total if total.strip() else "0"
            if active_col.isnumeric():
                active = row[int(active_col) - 1]
                active = active if active.strip() else "0"
            if deaths_per_mil_col.isnumeric():
                deaths_per_mil = row[int(deaths_per_mil_col) - 1]
                deaths_per_mil = deaths_per_mil if deaths_per_mil.strip() else "0"
            if total_per_mil_col.isnumeric():
                total_per_mil = row[int(total_per_mil_col) - 1]
                total_per_mil = total_per_mil if total_per_mil.strip() else "0"
            if total_tests_col.isnumeric():
                total_tests = row[int(total_tests_col) - 1]
                total_tests = total_tests if total_tests.strip() else "0"
            if death_col.isnumeric():
                deceased = row[int(death_col) - 1]
                deceased = deceased if deceased.strip() else "0"
            if recovered_col.isnumeric():
                recovered = row[int(recovered_col) - 1]
                recovered = recovered if recovered.strip() else "0"
            d = dict(country=country,
                     region=region,
                     infected=total,
                     deaths=deceased,
                     recoveries=recovered,
                     active=active,
                     total_per_mil=total_per_mil,
                     deaths_per_mil=deaths_per_mil,
                     total_tests=total_tests)
            result.append(d)
        return result


if __name__ == '__main__':
    print(d)