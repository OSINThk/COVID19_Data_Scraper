from Scraper import Scraper
import datetime
from utils import sanitize_digit


class WorldoMeterService(object):
    def __init__(self):
        self.url = "https://www.worldometers.info/coronavirus/#countries"
        self.scraper = Scraper(url=self.url)
        self.last_updated = datetime.datetime.utcnow()

    def get_global_stats(self):
        print(f"Fetching global stats.")
        self.scraper = Scraper(
            url="https://www.worldometers.info/coronavirus/#countries")
        table = self.search_table_by_id('main_table_countries_today')
        res = self.process_table(table, "9", "-8", "2", "3", "5", "7", "8", "10", "11", "12", "4", "6", "14")
        return res

    def get_us_stats(self):
        self.scraper = Scraper(
            url="https://www.worldometers.info/coronavirus/country/us/")
        table = self.search_table_by_id('usa_table_countries_today')
        res = self.process_country_table(table, "USA", "3", "-11", "1", "2", "4", "", "6")
        return res

    def search_table(self, text, index=0):
        table = self.scraper.find_table_with_text(text, index)
        lst = self.scraper.table_to_2d_list(table)
        return lst

    def search_table_by_id(self, table_id):
        table = self.scraper.find_table_by_id(table_id)
        lst = self.scraper.table_to_2d_list(table)
        return lst

    def process_country_table(self, table, country, start_row, end_row, region_col, total_col, death_col, recovered_col,
                              active_col):
        if start_row.isnumeric():
            table = table[int(start_row) - 1:]
        if end_row.lstrip('-+').isnumeric():
            table = table[:int(end_row)]
        result = []
        for row in table:
            region = row[int(region_col) - 1]
            total = deceased = recovered = active = "0"
            if total_col.isnumeric():
                total = row[int(total_col) - 1]
                total = total if total.strip() else "0"
            if active_col.isnumeric():
                active = row[int(active_col) - 1]
                active = active if active.strip() else "0"
            if death_col.isnumeric():
                deceased = row[int(death_col) - 1]
                deceased = deceased if deceased.strip() else "0"
            if recovered_col.isnumeric():
                recovered = row[int(recovered_col) - 1]
                recovered = recovered if recovered.strip() else "0"
            else:
                try:
                    recovered = str(int(sanitize_digit(total)) - int(sanitize_digit(deceased)) - int(sanitize_digit(active)))
                except Exception:
                    print(region, total, deceased, active)
            d = dict(country=country,
                     region=region,
                     infected=total,
                     deaths=deceased,
                     recoveries=recovered,
                     active=active,
                     last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            result.append(d)
        return result

    def process_table(self, table, start_row, end_row, country_col, total_col, death_col, recovered_col,
                      active_col, total_per_mil_col, deaths_per_mil_col, total_tests_col, new_cases_col,
                      new_deaths_col, population_col):
        if start_row.isnumeric():
            table = table[int(start_row) - 1:]
        if end_row.lstrip('-+').isnumeric():
            table = table[:int(end_row)]
        result = []
        region = ""
        for row in table:
            try:
                country = row[int(country_col) - 1]
                total = deceased = recovered = active = total_per_mil = total_tests = deaths_per_mil = "0"
                active_per_mil = recovered_per_mil = tests_per_mil = new_cases = new_deaths = pop = "0"
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
                if population_col.isnumeric():
                    pop = row[int(population_col) - 1]
                    pop = pop if pop.strip() else "0"
                if pop != "0":
                    population_per_mil = int(sanitize_digit(pop)) / 1000000
                    if population_per_mil>0:
                        active_per_mil = int(int(sanitize_digit(active)) / population_per_mil)
                        recovered_per_mil = int(int(sanitize_digit(recovered)) / population_per_mil)
                        tests_per_mil = int(int(sanitize_digit(total_tests)) / population_per_mil)
                if new_cases_col.isnumeric():
                    new_cases = row[int(new_cases_col) - 1]
                    new_cases = sanitize_digit(new_cases) if new_cases.strip() else "0"
                if new_deaths_col.isnumeric():
                    new_deaths = row[int(new_deaths_col) - 1]
                    new_deaths = sanitize_digit(new_deaths) if new_deaths.strip() else "0"
                d = dict(country=country,
                         region=region,
                         infected=total,
                         deaths=deceased,
                         recoveries=recovered,
                         active=active,
                         total_per_mil=total_per_mil,
                         deaths_per_mil=deaths_per_mil,
                         total_tests=total_tests,
                         active_per_mil=active_per_mil,
                         recovered_per_mil=recovered_per_mil,
                         tests_per_mil=tests_per_mil,
                         new_cases=new_cases,
                         new_deaths=new_deaths,
                         pop=pop,
                         last_updated=self.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
                result.append(d)
            except Exception as e:
                print(row, e)
        return result


if __name__ == '__main__':
    a = WorldoMeterService()
    a.get_us_stats()
