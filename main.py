import re
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium import webdriver
import pandas as pd

from tqdm import tqdm

cookie = 'HWWAFSESID=f9d1669af2d96dd538c; HWWAFSESTIME=1667707406135; csrfToken=XKWfFWwbUGRPhgDQy9IUdaxw; jsid=SEO-BING-ALL-SY-000001; TYCID=f88d47905d8711ed9181a7f78b21a612; sajssdk_2015_cross_new_user=1; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1667707410; show_activity_id_68=68; bannerFlag=true; _bl_uid=nvla9a4g4aCu8z1v53zXm6zm1ma0; ssuid=8622307960; _ga=GA1.2.198841016.1667707575; _gid=GA1.2.2098702406.1667707575; sensorsdata2015jssdkcross={"distinct_id":"285334348","first_id":"1844b1b93f4a38-0df59b0131a7a58-7d5d5474-1327104-1844b1b93f58be","props":{"$latest_traffic_source_type":"自然搜索流量","$latest_search_keyword":"未取到值","$latest_referrer":"https://cn.bing.com/"},"identities":"eyIkaWRlbnRpdHlfbG9naW5faWQiOiIyODUzMzQzNDgiLCIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg0NGIxYjkzZjRhMzgtMGRmNTliMDEzMWE3YTU4LTdkNWQ1NDc0LTEzMjcxMDQtMTg0NGIxYjkzZjU4YmUifQ==","history_login_id":{"name":"$identity_login_id","value":"285334348"},"$device_id":"1844b1b93f4a38-0df59b0131a7a58-7d5d5474-1327104-1844b1b93f58be"}; RTYCID=79b80cb4d73248f5a49c0c84680e0a40; cloud_token=40ab312e7c434f208dd3e0d671273fa5; tyc-user-info={"state":"0","vipManager":"0","mobile":"18056199338"}; tyc-user-info-save-time=1667716268633; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODA1NjE5OTMzOCIsImlhdCI6MTY2NzcxNjI2OCwiZXhwIjoxNjcwMzA4MjY4fQ.zvIeBcvj0yG96Q-Zqd8m9gtstTPjhYIBuqhDp1sHlcAsRYtOkoOic0SeI32Sjk_dCk1crGvmZTOAfbOvxFxYdw; searchSessionId=1667716381.17750449; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1667716398'

headers = {
    'Cookie': cookie.encode('utf-8')
    ,
    'Connection': 'close',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}

all_companys = pd.read_excel('data.xlsx')
key_words = all_companys['企业名称'].to_list()[:1000]
exist = []
# key_words = ['ACI（天津）模具有限公司', 'BPW（梅州）车轴有限公司']
num = 0
hrefs = []

requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接

option = webdriver.ChromeOptions()
# option.add_argument("headless")
browser = webdriver.Chrome(chrome_options=option)
for key_word in tqdm(key_words, desc="获取网址", file=sys.stdout):
    url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word))
    browser.get(url)
    browser.implicitly_wait(1)
    company = browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")
    if company.text == key_word:
        href = company.get_attribute('href')
        hrefs.append({"company_name": company.text, "url": href})
        exist.append(1)
    else:
        exist.append(0)
print(sum(exist))

for index, href in tqdm(enumerate(hrefs), desc="获取信息", file=sys.stdout):
    browser.get(href['url'])
    browser.implicitly_wait(1)

    # 股东信息部分
    GuDongInfo = pd.DataFrame()
    gudongs = []
    GuDong = browser.find_elements_by_class_name('index_lazy-img-toco__EU_FE')  # 股东
    for item in GuDong:
        gudongs.append(item.text)

    GuDong_size = len(gudongs)

    chigubilis = []
    for i in range(GuDong_size):
        ChiGuBiLi = browser.find_element_by_xpath(
            f'//*[@id="page-root"]/div[3]/div[1]/div[3]/div/div[2]/div[2]/div/div[6]/div/div[2]/div/table/tbody/tr[{i + 1}]/td[3]/div')
        chigubilis.append(ChiGuBiLi.text)

    GuDongInfo['企业名称'] = [href['company_name']] * GuDong_size
    GuDongInfo['股东(发起人)'] = gudongs
    GuDongInfo['持股比例'] = chigubilis
    if index == 0:
        GuDongInfo.to_csv("test.csv", mode='w', header=True, index=False)
    else:
        GuDongInfo.to_csv("test.csv", mode='a', header=False, index=False)

#
#     # 对外投资部分
#     beitouzis = []
#     temp = browser.find_elements_by_class_name("right-name")
#     for item in temp:
#         tempp = item.find_elements_by_class_name('link-click')
#         beitouzis.append(tempp)
#
#     print(beitouzis)
