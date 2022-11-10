import sys
from time import sleep
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from tqdm import tqdm


class crawler:
    def __init__(self):
        self.all_companys = pd.read_excel('dataset/data.xlsx')
        self.key_words = self.all_companys['企业名称'].to_list()[100:120]  # 在这
        # self.key_words = ['万源市金桥建材有限责任公司']
        # key_words = ['七台河矿业精煤集团有限公司']
        self.exist = []  # 能否匹配到网址
        self.num = 0
        self.DealTimeOut_max_times = 0
        self.hrefs = []  # 匹配到的企业名称和网址(字典格式存储)
        self.unable_1 = []  # 查找不到网址
        self.unable_2 = []  # 无股东信息
        self.unable_3 = []  # 已注销
        self.unable_4 = []  # 超时未被获取
        self.unable_5 = []  # 未知原因未被获取

        option = webdriver.ChromeOptions()
        # option.add_argument("headless")   # 取消注释可以不显示弹出的chrome浏览器
        self.browser = webdriver.Chrome(chrome_options=option)

    def GetURL(self):
        for key_word in tqdm(self.key_words, desc="获取网址", file=sys.stdout):
            url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word))
            self.browser.get(url)
            self.browser.implicitly_wait(1)

            company = self.browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")
            LogOut = company.find_element_by_xpath("../../div[2]")
            if LogOut.text == "注销":
                print(key_word, "已被注销")
                self.exist.append(0)
                self.unable_3.append(key_word)
                continue

            if company.text == key_word or company.text == key_word[:-2] + '责任公司' or key_word in company.text:
                href = company.get_attribute('href')
                self.hrefs.append({"company_name": key_word, "url": href})
                self.exist.append(1)
            else:
                try:
                    temp = self.browser.find_element_by_xpath("//*[contains(text(),'历史名称')]")
                    previous_url = temp.find_element_by_xpath("../../../div[1]/div[1]/a").get_attribute('href')
                    self.hrefs.append({"company_name": key_word, "url": previous_url})
                    self.exist.append(1)
                except:
                    url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word[:-2] + '责任公司'))
                    self.browser.get(url)
                    WebDriverWait(self.browser, 10)  # 等网站加载好，最多等10s
                    company = self.browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")

                    LogOut = company.find_element_by_xpath("../../div[2]")
                    if LogOut.text == "注销":
                        print(key_word, "已被注销")
                        self.exist.append(0)
                        self.unable_3.append(key_word)
                        continue

                    if company.text == key_word or company.text == key_word[:-2] + '责任公司':
                        href = company.get_attribute('href')
                        self.hrefs.append({"company_name": key_word, "url": href})
                        self.exist.append(1)
                    else:
                        print("未找到:", key_word)
                        self.unable_1.append(key_word)
                        self.exist.append(0)
        print(f"共匹配到:{sum(self.exist)}个")
        # 这个exist数组后面可以写入data.xlsx的一列，用以表示存不存在

        with open("res/unable_1.txt", "w") as f:
            for item in self.unable_1:
                f.write(item)
                f.write('\n')
            f.close()

        with open("res/unable_3.txt", "w") as f:
            for item in self.unable_3:
                f.write(item)
                f.write('\n')
            f.close()

    def GetHolderInfo(self, hrefs, sign):
        if sign == 0:
            if os.path.isfile("res/unable_2.txt"):  # 如果有unable_2.txt就删掉
                os.remove("res/unable_2.txt")

        for href in tqdm(hrefs, desc="获取信息", file=sys.stdout):
            self.browser.get(href['url'])
            self.browser.implicitly_wait(3)

            # 股东信息部分
            GuDongInfo = pd.DataFrame()

            # 在上方索引栏定位股东信息
            try:
                self.browser.find_element_by_xpath(
                    '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
            except:  # 如果在索引栏没有找到说明无股东信息
                print(href['company_name'], "无股东信息")
                self.unable_2.append(href['company_name'])

                continue

            # 在正文获取股东模块
            gudongs = []  # 股东
            chigubilis = []  # 持股比例

            GuDong = self.browser.find_elements_by_xpath("//div[@data-dim='holder']/div[2]/div/table/tbody/tr")
            WebDriverWait(self.browser, 10)
            GuDong_size = len(GuDong)
            try:
                for item in GuDong:
                    WebDriverWait(self.browser, 10)
                    data = item.find_elements_by_xpath("./td")
                    WebDriverWait(self.browser, 10)
                    gudongs.append(data[1].find_element_by_xpath("./div/div[2]/div/div/a").text)
                    chigubilis.append(data[2].text)
            except:
                print(href['company_name'], "超时未被获取")
                self.unable_4.append(href)
                continue

            if len(gudongs) == 0 or len(chigubilis) == 0:
                print(href['company_name'],"未知原因缺失")
                self.unable_5.append(href)
                continue
            else:
                GuDongInfo['企业名称'] = [href['company_name']] * GuDong_size
                GuDongInfo['股东(发起人)'] = gudongs
                GuDongInfo['持股比例'] = chigubilis
                if sign == 0:
                    GuDongInfo.to_csv("res/result.csv", mode='w', header=True, index=False)
                else:
                    GuDongInfo.to_csv("res/result.csv", mode='a', header=False, index=False)
                sign = 1

        with open("res/unable_2.txt", "w") as f:
            for item in self.unable_2:
                f.write(item)
                f.write('\n')
            f.close()

        with open("res/unable_4.txt", 'w') as f:
            for item in self.unable_4:
                f.write(str(item))
                f.write('\n')
            f.close()

        with open("res/unable_5.txt", 'w') as f:
            for item in self.unable_5:
                f.write(str(item))
                f.write('\n')
            f.close()

    def DealTimeOut(self):
        print("\n处理超时文件")
        deal = []
        with open("res/unable_4.txt", "r") as f:
            data = f.read().strip().split('\n')
            print(data)
            for item in data:
                if not item == '':
                    deal.append(eval(item))
            f.close()
        self.GetHolderInfo(deal, 1)

    def DealUnKnown(self):
        print("\n处理未知原因空缺")
        deal = []
        with open("res/unable_5.txt", "r") as f:
            data = f.read().strip().split('\n')
            for item in data:
                if not item == '':
                    deal.append(eval(item))
            f.close()
        self.GetHolderInfo(deal, 1)


if __name__ == '__main__':
    c = crawler()
    c.GetURL()
    c.GetHolderInfo(c.hrefs, 0)
    c.DealTimeOut()
    c.DealUnKnown()
