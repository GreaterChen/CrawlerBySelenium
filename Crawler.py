import pickle
import sys
from time import sleep
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from tqdm import tqdm


class Crawler:
    def __init__(self):
        self.unable_1 = []  # 查找不到网址
        self.unable_2 = []  # 无所需信息
        self.unable_3 = []  # 已注销
        self.unable_4 = []  # 超时未被获取
        self.unable_5 = []  # 未知原因未被获取

        self.DealTimeOut_times = 0  # 处理超时的次数
        self.DealUnKnown_times = 0  # 处理未知原因缺失的次数

        option = webdriver.ChromeOptions()
        option.add_argument("headless")  # 注释可以显示chrome浏览器
        option.add_argument('no-sandbox')
        option.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
        # 本地运行用第一行，linux服务器运行用第二行
        # self.browser = webdriver.Chrome(chrome_options=option)
        self.browser = webdriver.Chrome(options=option, executable_path='/root/chromedriver')
        # self.browser.maximize_window()

    def LogIn(self):
        self.browser.get("https://www.tianyancha.com/company/23402373")
        cookies = pickle.load(open("cookie.pkl", "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
