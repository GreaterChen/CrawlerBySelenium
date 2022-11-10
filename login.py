import requests
from selenium import webdriver
import pickle

option = webdriver.ChromeOptions()
# option.add_argument("headless")
browser = webdriver.Chrome(chrome_options=option)
browser.get("https://www.tianyancha.com/company/23402373")
# pickle.dump(browser.get_cookies(),open("cookie.pkl","wb"))
cookies = pickle.load(open("cookie.pkl", "rb"))
for cookie in cookies:
    browser.add_cookie(cookie)
browser.get("https://www.tianyancha.com/company/23402373")
pass