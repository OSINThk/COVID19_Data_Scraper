from lxml import html
import requests
from Xpaths import Xpaths


class CovidGraph(object):
    def __init__(self, html_string=None):
        if html_string is not None:
            self.tree = html.fromstring(html_string)

    def process_url(self, url):
        r = requests.get(url)
        html_string = r.content
        self.tree = html.fromstring(html_string)
        table = self.tree.xpath(Xpaths.table_xpath)[0]
        self.process_table(table)

    def extract_table(self):
        table = self.tree.xpath(Xpaths.table_xpath)
        if table:
            return table[0]

    @staticmethod
    def process_row(row):
        date = row.xpath(Xpaths.td_date)
        bars = row.xpath(Xpaths.td_bar)
        if date is None or bars is None:
            raise Exception("date/bars not found")
        d = []
        for el in bars:
            d.append(el.get('title'))
        date_str = date[0].text or ""
        return date_str, d

    def process_table(self, table, debug=False):
        rows = table.xpath(Xpaths.table_rows)
        for i, row in enumerate(rows):
            try:
                date, bars = self.process_row(row)
                death_str = f"Deaths: {bars[0]}"
                recovered_str = f"Recovered: {bars[1]}"
                active_cases = f"Active Cases: {bars[2]}"
                if len(date) < 4:
                    date = date + '\t'
                print(f"{date}\t{death_str}\t{recovered_str}\t{active_cases}")
            except Exception as e:
                if debug:
                    print(i, e)
