import requests
from bs4 import BeautifulSoup
from itertools import product


class Scraper(object):
    def __init__(self, html_string=None, url=None):
        if url is not None:
            html_string = requests.get(url).content
        if html_string is not None:
            self.soup = BeautifulSoup(html_string, features="lxml")

    def find_table_with_text(self, string, index=0):
        tables = self.soup.findAll("table")
        res = []
        for i, table in enumerate(tables):
            if string in str(table):
                res.append(table)
        return res[index] if res else None

    def find_table_by_id(self, table_id):
        return self.soup.find("table", {"id": table_id})

    def table_to_2d_list(self, table_tag):
        rowspans = []
        rows = table_tag.find_all('tr')
        colcount = 0
        for r, row in enumerate(rows):
            cells = row.find_all(['td', 'th'], recursive=False)
            colcount = max(
                colcount,
                sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
            rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
            rowspans = [s - 1 for s in rowspans if s > 1]
        table = [[None] * colcount for row in rows]
        rowspans = {}
        for row, row_elem in enumerate(rows):
            span_offset = 0
            for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
                col += span_offset
                while rowspans.get(col, 0):
                    span_offset += 1
                    col += 1
                rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
                colspan = int(cell.get('colspan', 1)) or colcount - col
                span_offset += colspan - 1
                value = cell.get_text().strip()
                for drow, dcol in product(range(rowspan), range(colspan)):
                    try:
                        table[row + drow][col + dcol] = value
                        rowspans[col + dcol] = rowspan
                    except IndexError:
                        pass
            rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}
        return table
