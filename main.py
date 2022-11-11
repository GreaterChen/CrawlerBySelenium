import pickle
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
        self.key_words = self.all_companys['企业名称'].to_list()[:105]  # 在这更改处理企业范围
        # self.key_words = ['万源市康星饮料矿泉水有限公司']
        self.exist = []  # 能否匹配到网址
        self.num = 0
        self.DealTimeOut_max_times = 0
        self.DealUnKnown_max_times = 0
        self.hrefs = []  # 匹配到的企业名称和网址(字典格式存储)
        self.unable_1 = []  # 查找不到网址
        self.unable_2 = []  # 无股东信息
        self.unable_3 = []  # 已注销
        self.unable_4 = []  # 超时未被获取
        self.unable_5 = []  # 未知原因未被获取

        option = webdriver.ChromeOptions()
        # option.add_argument("headless")  # 注释可以显示chrome浏览器
        option.add_argument('no-sandbox')
        option.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
        # 本地运行用第一行，linux服务器运行用第二行
        self.browser = webdriver.Chrome(chrome_options=option)
        self.browser.maximize_window()
        # self.browser = webdriver.Chrome(options=option, executable_path='/root/chromedriver')
        self.LogIn()

    def LogIn(self):
        self.browser.get("https://www.tianyancha.com/company/23402373")
        cookies = pickle.load(open("cookie.pkl", "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)

    def GetURL(self):
        cnt = 0
        save_info = pd.DataFrame()
        names = []
        urls = []
        status = []  # 0:正常，1:经营状况异常，
        for key_word in tqdm(self.key_words, desc="获取网址", file=sys.stdout):
            raw_word = key_word
            names.append(key_word)
            url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word))
            self.browser.get(url)
            self.browser.implicitly_wait(1)
            company = self.browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")  # 获取搜索结果的第一家企业
            if company.text == key_word or company.text == key_word[:-2] + '责任公司' or key_word in company.text \
                    or company.text == key_word.replace('（', '').replace('）', '') \
                    or company.text == (key_word[:-2] + '责任公司').replace('（', '').replace('）', ''):
                try:  # 尝试能否获取到企业经营状态(有毫无信息的企业)
                    LogOut = company.find_element_by_xpath("../../div[2]").get_attribute('class')
                    if 'normal' not in LogOut:  # 判断经营状况是否正常
                        print("经营状况异常:", key_word)
                        self.exist.append(0)
                        self.unable_3.append(key_word)
                        urls.append('-')
                        status.append(1)
                        continue
                    href = company.get_attribute('href')
                    self.hrefs.append({"company_name": key_word, "url": href})
                    self.exist.append(1)
                    urls.append(href)
                    status.append(0)
                    continue
                except:
                    pass

            try:  # 尝试能否找到历史名称匹配的企业
                temp = self.browser.find_element_by_xpath("//*[contains(text(),'历史名称')]")
                previous_name = temp.find_element_by_xpath("../span[2]").text
                if previous_name == key_word or previous_name == key_word[:-2] + '责任公司' or key_word in previous_name\
                        or key_word[:-2] + '责任公司' in previous_name\
                        or previous_name == key_word.replace('（', '').replace('）', '') \
                        or previous_name == (key_word[:-2] + '责任公司').replace('（', '').replace('）', ''):
                    company = temp.find_element_by_xpath("../../../div[1]/div[1]/a")
                    try:
                        LogOut = company.find_element_by_xpath("../../div[2]").get_attribute('class')
                        if 'normal' not in LogOut:  # 判断经营状况是否正常
                            print("经营状况异常:", key_word)
                            self.exist.append(0)
                            self.unable_3.append(key_word)
                            status.append(1)
                            urls.append('-')
                            continue
                        href = company.get_attribute('href')
                        self.hrefs.append({"company_name": key_word, "url": href})
                        self.exist.append(1)
                        status.append(0)
                        urls.append(href)
                        continue
                    except:
                        pass
            except:
                key_word = key_word[:-2] + '责任公司'
                url = 'https://www.tianyancha.com/search?key={}'.format(quote(key_word))
                self.browser.get(url)
                WebDriverWait(self.browser, 10)  # 等网站加载好，最多等10s
                company = self.browser.find_element_by_xpath("//*[@class='index_name__qEdWi']/a")
                if company.text == key_word or key_word in company.text \
                        or company.text == key_word.replace('（', '').replace('）', ''):
                    try:
                        LogOut = company.find_element_by_xpath("../../div[2]").get_attribute('class')
                        if 'normal' not in LogOut:  # 判断经营状况是否正常
                            print("经营状况异常:", raw_word)
                            self.exist.append(0)
                            self.unable_3.append(raw_word)
                            status.append(1)
                            urls.append('-')
                            continue
                        href = company.get_attribute('href')
                        self.hrefs.append({"company_name": raw_word, "url": href})
                        self.exist.append(1)
                        status.append(0)
                        urls.append(href)
                        continue
                    except:
                        pass
                try:  # 尝试能否找到历史名称匹配的企业
                    temp = self.browser.find_element_by_xpath("//*[contains(text(),'历史名称')]")

                    previous_name = temp.find_element_by_xpath("../span[2]").text
                    if previous_name == key_word or key_word in previous_name\
                            or previous_name == key_word.replace('（', '').replace('）', ''):
                        company = temp.find_element_by_xpath("../../../div[1]/div[1]/a")
                        try:
                            LogOut = company.find_element_by_xpath("../../div[2]").get_attribute('class')
                            if 'normal' not in LogOut:  # 判断经营状况是否正常
                                print("经营状况异常:", raw_word)
                                self.exist.append(0)
                                self.unable_3.append(raw_word)
                                status.append(1)
                                urls.append('-')
                                continue
                            href = company.get_attribute('href')
                            self.hrefs.append({"company_name": raw_word, "url": href})
                            self.exist.append(1)
                            status.append(1)
                            urls.append(href)
                            continue
                        except:
                            pass
                except:
                    pass
            status.append(2)
            urls.append('-')
            print('未找到:', raw_word)
            cnt += 1
            if cnt % 100 == 0:
                save_info['企业名称'] = names
                save_info['状态'] = status
                save_info['网址'] = urls
                save_info.to_csv('res/url_info.csv')

        print(f"共匹配到:{sum(self.exist)}个")
        # 这个exist数组后面可以写入data.xlsx的一列，用以表示存不存在

        save_info['企业名称'] = names
        save_info['状态'] = status
        save_info['网址'] = urls
        save_info.to_csv('res/url_info.csv')

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
        self.unable_4.clear()
        self.unable_5.clear()
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
                gudong_title = self.browser.find_element_by_xpath(
                    '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
                total_len = int(gudong_title.find_element_by_xpath("./span").text)
                pass
            except:  # 如果在索引栏没有找到说明无股东信息
                print("无股东信息:", href['company_name'])
                self.unable_2.append(href['company_name'])
                continue

            # 在正文获取股东模块
            gudongs = []  # 股东
            chigubilis = []  # 持股比例

            # GuDong_size = len(GuDong)
            page = int(total_len / 20) + 1
            current_page = 0
            try:
                while page != current_page:
                    if current_page != 0:
                        temp = self.browser.find_element_by_xpath(
                            f"//div[@data-dim='holder']/div[2]/div/div[@class='table-footer']/div/div/div/div[{current_page + 1}]")
                        self.browser.execute_script("arguments[0].click();", temp)
                    sleep(1)
                    self.GuDong = self.browser.find_elements_by_xpath(
                        "//div[@data-dim='holder']/div[2]/div/table/tbody/tr")
                    WebDriverWait(self.browser, 10)
                    for item in self.GuDong:
                        WebDriverWait(self.browser, 10)
                        data = item.find_elements_by_xpath("./td")
                        WebDriverWait(self.browser, 20).until(
                            lambda diver: data[1].find_element_by_xpath("./div/div[2]/div/div/a"))
                        gudongs.append(data[1].find_element_by_xpath("./div/div[2]/div/div/a").text)
                        chigubilis.append(data[2].text)
                    current_page += 1
            except:
                print("超时未获取:", href['company_name'])
                self.unable_4.append(href)
                continue

            if len(gudongs) == 0 or len(chigubilis) == 0 or gudongs[0] == '' or chigubilis[0] == '':
                print("未知原因缺失:", href['company_name'])
                self.unable_5.append(href)
                continue
            else:
                GuDongInfo['企业名称'] = [href['company_name']] * total_len
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

        if len(self.unable_4) and self.DealTimeOut_max_times <= 5:
            self.DealTimeOut_max_times += 1
            self.DealTimeOut()

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

        if len(self.unable_5) and self.DealUnKnown_max_times <= 5:
            self.DealUnKnown_max_times += 1
            self.DealUnKnown()


if __name__ == '__main__':
    c = crawler()
    c.GetURL()
    # c.GetHolderInfo(c.hrefs, 0)
    # c.DealTimeOut()
    # c.DealUnKnown()
