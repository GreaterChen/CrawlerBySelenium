import pandas as pd

from Crawler import *

begin = 0
end = 10000


class GetHolderInfo(Crawler):
    def __init__(self, begin, end):
        super(GetHolderInfo, self).__init__()
        url_info = pd.read_csv('res/url/url_info_total.csv')
        name = url_info[url_info['状态'] == 0]['企业名称'].to_list()
        url = url_info[url_info['状态'] == 0]['网址'].to_list()
        max_len = len(name)
        print(f"共有{max_len}条数据")
        if begin >= max_len:
            print("超出索引,请确认是赋值错误还是已全部结束")
            return
        if end >= max_len:
            end = max_len

        self.hrefs = []
        for i in range(begin, end):
            self.hrefs.append({'company_name': name[i], "url": url[i]})
        self.LogIn()

    def run(self, hrefs, sign, sleep_time):
        self.unable_4.clear()
        self.unable_5.clear()

        for href in tqdm(hrefs, desc="获取股东信息", file=sys.stdout):
            self.DealUnKnown_times = 0
            self.browser.get(href['url'])
            self.browser.implicitly_wait(1)
            while True:
                self.DealUnKnown_times += 1
                unknown_sign = 0
                # 在上方索引栏定位股东信息
                try:
                    WebDriverWait(self.browser, 0.1).until(
                        lambda diver: self.browser.find_element_by_xpath(
                            '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]'))
                    gudong_title = self.browser.find_element_by_xpath(
                        '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
                    if gudong_title.text[:4] != '股东信息':  # 可能会匹配到'历史股东信息'
                        print("无股东信息:", href['company_name'], href['url'])
                        self.unable_2.append(href['company_name'])
                        break
                    total_len = int(gudong_title.find_element_by_xpath("./span").text)
                except:  # 如果在索引栏没有找到说明无股东信息
                    print("无股东信息:", href['company_name'], href['url'])
                    self.unable_2.append(href['company_name'])
                    break

                WebDriverWait(self.browser, 3).until(
                    lambda diver: self.browser.find_element_by_xpath(
                        "//div[@data-dim='holder']/div[2]/div/table/tbody/tr"))

                # 在正文获取股东模块
                page = int((total_len - 1) / 20) + 1
                current_page = 0

                self.DealTimeOut_times = 0
                sleep_time = 0.5
                while True:
                    gudongs = []
                    chigubilis = []
                    self.DealTimeOut_times += 1
                    try:
                        while page != current_page:
                            if current_page == 1:
                                temp = self.browser.find_element_by_xpath(
                                    f"//div[@data-dim='holder']/div[2]/div/div[@class='table-footer']/div/div/div/div[{page + 1}]")
                                self.browser.execute_script("arguments[0].click();", temp)
                            elif current_page > 1:
                                temp = self.browser.find_element_by_xpath(
                                    f"//div[@data-dim='holder']/div[2]/div/div[@class='table-footer']/div/div/div/div[{page + 2}]")
                                self.browser.execute_script("arguments[0].click();", temp)
                            sleep(sleep_time)
                            WebDriverWait(self.browser, 3).until(
                                lambda diver: self.browser.find_element_by_xpath(
                                    "//div[@data-dim='holder']/div[2]/div/table/tbody/tr"))
                            self.GuDong = self.browser.find_elements_by_xpath(
                                "//div[@data-dim='holder']/div[2]/div/table/tbody/tr")
                            for item in self.GuDong:
                                WebDriverWait(self.browser, 3).until(
                                    lambda diver: item.find_element_by_xpath("./td"))
                                data = item.find_elements_by_xpath("./td")
                                WebDriverWait(self.browser, 3).until(
                                    lambda diver: data[1].find_element_by_xpath("./div/div[2]/div/div"))
                                gudongs.append(data[1].find_element_by_xpath("./div/div[2]/div/div").text)
                                chigubilis.append(data[2].text)
                            current_page += 1
                    except:
                        if self.DealTimeOut_times <= 3:
                            sleep_time += 0.2
                            continue
                        else:
                            print("超时未获取:", href['company_name'], href['url'])
                            self.unable_4.append(href)
                            break

                    if len(gudongs) == 0 or len(chigubilis) == 0 or gudongs[0] == '' or chigubilis[0] == '':
                        if self.DealUnKnown_times <= 5:
                            unknown_sign = 1
                            break
                        else:
                            print("未知原因缺失:", href['company_name'], href['url'])
                            self.unable_5.append(href)
                            unknown_sign = 0
                            break
                    else:
                        GuDongInfo = pd.DataFrame()
                        GuDongInfo['企业名称'] = [href['company_name']] * len(gudongs)
                        GuDongInfo['股东(发起人)'] = gudongs
                        GuDongInfo['持股比例'] = chigubilis
                        GuDongInfo.to_csv("res/Holder/result.csv", mode='a', header=False, index=True)
                        break

                if unknown_sign == 0:
                    break

        # 无股东信息
        with open("res/Holder/unable_2.txt", "a") as f:
            for item in self.unable_2:
                f.write(item)
                f.write('\n')
            f.close()

        # 超时
        with open("res/Holder/unable_4.txt", 'a') as f:
            for item in self.unable_4:
                f.write(str(item))
                f.write('\n')
            f.close()

        # 未知原因
        unknown = pd.DataFrame()
        name = []
        url = []
        status = []
        for item in self.unable_5:
            name.append(item['company_name'])
            url.append(item['url'])
            status.append(0)
        unknown['企业名称'] = name
        unknown['状态'] = status
        unknown['网址'] = url
        unknown.to_csv("res/Holder/unknown.csv", mode='w')


if __name__ == '__main__':
    hrefs = [{'company_name': '四川长江液压件有限公司', 'url': 'https://www.tianyancha.com/company/187064686'},
             {'company_name': '长春市汽车冲压件有限公司', 'url': 'https://www.tianyancha.com/company/270553316'}
             ]
    g = GetHolderInfo(begin, end)
    g.run(g.hrefs, 0, 0.1)
