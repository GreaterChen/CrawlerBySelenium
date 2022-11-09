from selenium import webdriver
from urllib.parse import quote


option = webdriver.ChromeOptions()
# option.add_argument("headless")
browser = webdriver.Chrome(chrome_options=option)