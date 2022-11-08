import sys
from time import sleep
from urllib.parse import quote
from selenium import webdriver
import pandas as pd

from tqdm import tqdm

# cookie = 'HWWAFSESID=f9d1669af2d96dd538c; HWWAFSESTIME=1667707406135; csrfToken=XKWfFWwbUGRPhgDQy9IUdaxw; jsid=SEO-BING-ALL-SY-000001; TYCID=f88d47905d8711ed9181a7f78b21a612; sajssdk_2015_cross_new_user=1; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1667707410; show_activity_id_68=68; bannerFlag=true; _bl_uid=nvla9a4g4aCu8z1v53zXm6zm1ma0; ssuid=8622307960; _ga=GA1.2.198841016.1667707575; _gid=GA1.2.2098702406.1667707575; sensorsdata2015jssdkcross={"distinct_id":"285334348","first_id":"1844b1b93f4a38-0df59b0131a7a58-7d5d5474-1327104-1844b1b93f58be","props":{"$latest_traffic_source_type":"自然搜索流量","$latest_search_keyword":"未取到值","$latest_referrer":"https://cn.bing.com/"},"identities":"eyIkaWRlbnRpdHlfbG9naW5faWQiOiIyODUzMzQzNDgiLCIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg0NGIxYjkzZjRhMzgtMGRmNTliMDEzMWE3YTU4LTdkNWQ1NDc0LTEzMjcxMDQtMTg0NGIxYjkzZjU4YmUifQ==","history_login_id":{"name":"$identity_login_id","value":"285334348"},"$device_id":"1844b1b93f4a38-0df59b0131a7a58-7d5d5474-1327104-1844b1b93f58be"}; RTYCID=79b80cb4d73248f5a49c0c84680e0a40; cloud_token=40ab312e7c434f208dd3e0d671273fa5; tyc-user-info={"state":"0","vipManager":"0","mobile":"18056199338"}; tyc-user-info-save-time=1667716268633; auth_token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODA1NjE5OTMzOCIsImlhdCI6MTY2NzcxNjI2OCwiZXhwIjoxNjcwMzA4MjY4fQ.zvIeBcvj0yG96Q-Zqd8m9gtstTPjhYIBuqhDp1sHlcAsRYtOkoOic0SeI32Sjk_dCk1crGvmZTOAfbOvxFxYdw; searchSessionId=1667716381.17750449; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1667716398'
#
# headers = {
#     'Cookie': cookie.encode('utf-8')
#     ,
#     'Connection': 'close',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
# }

all_companys = pd.read_excel('dataset/data.xlsx')
key_words = all_companys['企业名称'].to_list()
exist = []
# key_words = ['LG化学（广州）工程塑料有限公司']
# key_words = ['一汽实业绥中改装车厂']
num = 0
hrefs = []

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

index = 0
for href in tqdm(hrefs, desc="获取信息", file=sys.stdout):
    browser.get(href['url'])
    browser.implicitly_wait(3)
    # sleep(1)
    # 股东信息部分
    GuDongInfo = pd.DataFrame()

    # 在上方索引栏定位股东信息
    try:
        GuDong_title = browser.find_element_by_xpath(
            '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
    except:
        print('\n', href['company_name'], "无股东信息")
        continue

    # 在正文获取股东模块
    gudongs = []  # 股东
    chigubilis = []  # 持股比例

    GuDong = browser.find_elements_by_xpath("//div[@data-dim='holder']/div[2]/div/table/tbody/tr")

    GuDong_size = len(GuDong)
    for item in GuDong:
        data = item.find_elements_by_xpath("./td")
        gudongs.append(data[1].find_element_by_xpath("./div/div[2]/div/div/a").text)
        chigubilis.append(data[2].text)

    GuDongInfo['企业名称'] = [href['company_name']] * int(GuDong_size)
    GuDongInfo['股东(发起人)'] = gudongs
    GuDongInfo['持股比例'] = chigubilis
    if index == 0:
        GuDongInfo.to_csv("res/result.csv", mode='w', header=True, index=False)
    else:
        GuDongInfo.to_csv("res/result.csv", mode='a', header=False, index=False)

    index += 1

