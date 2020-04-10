from Scraper import Scraper


class WikipediaService(object):
    def __init__(self, country=None, url=None):
        if country is not None:
            self.country = country
        if url is not None:
            self.scraper = Scraper(url=url)

    def get_global_stats(self):
        print(f"Fetching global stats.")
        self.scraper = Scraper(
            url="https://en.m.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_pandemic_by_country_and_territory")
        res = self.process_table("Countries and territories", "2", "-2", "2", "3", "4", "5")
        return res

    def search_table(self, text, index=0):
        table = self.scraper.find_table_with_text(text, index)
        lst = self.scraper.table_to_2d_list(table)
        return lst

    def process_table(self, table_name, start_row, end_row, region_col, infected_col, death_col, recovered_col,
                      table_index=None):
        if type(table_index) == str and table_index.isnumeric():
            print(table_index)
            table = self.search_table(table_name, int(table_index) - 1)
        else:
            table = self.search_table(table_name)
        if start_row.isnumeric():
            table = table[int(start_row) - 1:]
        if end_row.lstrip('-+').isnumeric():
            table = table[:int(end_row)]
        result = []
        for row in table:
            region = row[int(region_col) - 1]
            infected = deceased = recovered = "0"
            if infected_col.isnumeric():
                infected = row[int(infected_col) - 1]
                infected = infected if infected.strip() else "0"
            if death_col.isnumeric():
                deceased = row[int(death_col) - 1]
                deceased = deceased if deceased.strip() else "0"
            if recovered_col.isnumeric():
                recovered = row[int(recovered_col) - 1]
                recovered = recovered if recovered.strip() else "0"
            d = [region, infected, deceased, recovered]
            result.append(d)
        return result
