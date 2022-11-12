from Crawler import *

# 欲爬取企业索引范围
begin = 0
end = 10000


class GetURL(Crawler):
    def __init__(self, begin, end):
        super(GetURL, self).__init__()
        self.all_companys = pd.read_excel('dataset/data.xlsx')
        self.key_words = self.all_companys['企业名称'].to_list()[begin:end]  # 在这更改处理企业范围
        self.exist = []  # 能否匹配到网址
        self.hrefs = []  # 匹配到的企业名称和网址(字典格式存储)
        self.unable_1 = []  # 查找不到网址
        self.unable_3 = []  # 经营状况异常

        self.LogIn()

    def run(self):
        cnt = 0
        save_info = pd.DataFrame()
        names = []
        urls = []
        status = []  # 0:正常，1:经营状况异常，2:未找到
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
                if previous_name == key_word or previous_name == key_word[:-2] + '责任公司' or key_word in previous_name \
                        or key_word[:-2] + '责任公司' in previous_name \
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
                    if previous_name == key_word or key_word in previous_name \
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
            self.unable_1.append(raw_word)
            cnt += 1
            if cnt % 100 == 0:
                save_info['企业名称'] = names
                save_info['状态'] = status
                save_info['网址'] = urls
                save_info.to_csv('res/url/url_info.csv', index=False)

        print(f"共匹配到:{sum(self.exist)}个")
        # 这个exist数组后面可以写入data.xlsx的一列，用以表示存不存在

        save_info['企业名称'] = names
        save_info['状态'] = status
        save_info['网址'] = urls
        if os.path.isfile("res/url/url_info_total.csv"):
            save_info.to_csv('res/url/url_info_total.csv', mode='a', header=False, index=False)
        else:
            save_info.to_csv('res/url/url_info_total.csv', mode='w', header=True, index=False)

        with open("res/url/unable_1.txt", "a") as f:
            for item in self.unable_1:
                f.write(item)
                f.write('\n')
            f.close()

        print("")

        with open("res/url/unable_3.txt", "a") as f:
            for item in self.unable_3:
                f.write(item)
                f.write('\n')
            f.close()


if __name__ == '__main__':
    r = GetURL(begin, end)
    r.run()
