import sys
from time import sleep
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from tqdm import tqdm

all_companys = pd.read_excel('dataset/data.xlsx')
key_words = all_companys['企业名称'].to_list()[100:120]
exist = []
# key_words = ['万源市金桥建材有限责任公司']
# key_words = ['七台河矿业精煤集团有限公司']
num = 0
hrefs = []

unable_1 = []  # 查找不到网址
unable_2 = []  # 无股东信息

option = webdriver.ChromeOptions()
# option.add_argument("headless")   # 取消注释可以不显示弹出的chrome浏览器
browser = webdriver.Chrome(chrome_options=option)
for key_word in tqdm(key_words, desc="获取网址", file=sys.stdout):
    url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word))
    browser.get(url)
    browser.implicitly_wait(1)

    company = browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")
    if company.text == key_word or company.text == key_word[:-2] + '责任公司' or key_word in company.text:
        href = company.get_attribute('href')
        hrefs.append({"company_name": key_word, "url": href})
        exist.append(1)
    else:
        try:
            temp = browser.find_element_by_xpath("//*[contains(text(),'历史名称')]")
            previous_url = temp.find_element_by_xpath("../../../div[1]/div[1]/a").get_attribute('href')
            hrefs.append({"company_name": key_word, "url": previous_url})
            exist.append(1)
        except:
            url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word[:-2] + '责任公司'))
            browser.get(url)
            WebDriverWait(browser, 10)  # 等网站加载好，最多等10s
            company = browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")
            if company.text == key_word or company.text == key_word[:-2] + '责任公司':
                href = company.get_attribute('href')
                hrefs.append({"company_name": key_word, "url": href})
                exist.append(1)
            else:
                print("未找到:", key_word)
                unable_1.append(key_word)
                exist.append(0)
print(f"共匹配到:{sum(exist)}个")
# 这个exist数组后面可以写入data.xlsx的一列，用以表示存不存在

with open("res/unable_1.txt", "w") as f:
    for item in unable_1:
        f.write(item)
        f.write('\n')

index = 0
unable_2_idx = 0
if os.path.isfile("res/unable_2.txt"):  # 如果有unable_2.txt就删掉
    os.remove("res/unable_2.txt")

for href in tqdm(hrefs, desc="获取信息", file=sys.stdout):
    browser.get(href['url'])
    browser.implicitly_wait(3)
    # 股东信息部分
    GuDongInfo = pd.DataFrame()

    # 在上方索引栏定位股东信息
    try:
        GuDong_title = browser.find_element_by_xpath(
            '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
    except:
        print('\n', href['company_name'], "无股东信息")
        unable_2.append(href['company_name'])
        if len(unable_2) % 5 == 0:  # 每攒5个存一下
            with open("res/unable_2.txt", "a"):
                while unable_2_idx < len(unable_2):
                    f.write(unable_2[unable_2_idx])
                    f.write('\n')
                    unable_2_idx += 1
        continue

    # 在正文获取股东模块
    gudongs = []  # 股东
    chigubilis = []  # 持股比例

    GuDong = browser.find_elements_by_xpath("//div[@data-dim='holder']/div[2]/div/table/tbody/tr")
    WebDriverWait(browser, 10)
    GuDong_size = len(GuDong)
    for item in GuDong:
        data = item.find_elements_by_xpath("./td")
        gudongs.append(data[1].find_element_by_xpath("./div/div[2]/div/div/a").text)
        chigubilis.append(data[2].text)

    GuDongInfo['企业名称'] = [href['company_name']] * GuDong_size
    GuDongInfo['股东(发起人)'] = gudongs
    GuDongInfo['持股比例'] = chigubilis
    if index == 0:
        GuDongInfo.to_csv("res/result.csv", mode='w', header=True, index=False)
    else:
        GuDongInfo.to_csv("res/result.csv", mode='a', header=False, index=False)
    index += 1

with open("res/unable_2.txt", "a") as f:    # 把最后不足5个的存一下
    while unable_2_idx < len(unable_2):
        f.write(unable_2[unable_2_idx])
        f.write('\n')
        unable_2_idx += 1
