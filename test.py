from time import sleep

from selenium import webdriver
from urllib.parse import quote
import pickle

option = webdriver.ChromeOptions()
# option.add_argument("headless")
browser = webdriver.Chrome(chrome_options=option)
browser.get("https://www.tianyancha.com/company/23402373")

cookies = pickle.load(open("cookie.pkl", "rb"))
for cookie in cookies:
    browser.add_cookie(cookie)
browser.get("https://www.tianyancha.com/company/23402373")

temp = browser.find_element_by_id("inverst-table")
temp = temp.find_element_by_xpath("./div/div[@class='table-footer']/div/div/div/div[2]").click()
pass
