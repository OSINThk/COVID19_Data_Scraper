class Xpaths(object):
    table_xpath = '//table[descendant::th[contains(text(), "COVID")]]'
    table_rows = './tbody/tr'
    td_date = "./td[1]"
    td_bar = "./td[2]/div"
