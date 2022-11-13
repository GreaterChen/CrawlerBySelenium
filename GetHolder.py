from Crawler import *

begin = 0
end = 10000


class GetHolderInfo(Crawler):
    def __init__(self, begin, end):
        super(GetHolderInfo, self).__init__()
        url_info = pd.read_csv('res/url/url_info_total.csv',encoding="ANSI")
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
        raw_sign = sign
        self.unable_4.clear()
        self.unable_5.clear()

        for href in tqdm(hrefs, desc="获取股东信息", file=sys.stdout):
            self.browser.get(href['url'])
            self.browser.implicitly_wait(1)

            # 股东信息部分
            GuDongInfo = pd.DataFrame()

            # 在上方索引栏定位股东信息
            try:
                gudong_title = self.browser.find_element_by_xpath(
                    '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"股东信息")]')
                if gudong_title.text[:4] != '股东信息':  # 可能会匹配到'历史股东信息'
                    print("无股东信息:", href['company_name'], href['url'])
                    self.unable_2.append(href['company_name'])
                    continue
                total_len = int(gudong_title.find_element_by_xpath("./span").text)

            except:  # 如果在索引栏没有找到说明无股东信息
                print("无股东信息:", href['company_name'], href['url'])
                self.unable_2.append(href['company_name'])
                continue

            # 在正文获取股东模块
            gudongs = []  # 股东
            chigubilis = []  # 持股比例

            # GuDong_size = len(GuDong)
            page = int(total_len / 21) + 1
            current_page = 0
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
                print("超时未获取:", href['company_name'], href['url'])
                self.unable_4.append(href)
                continue
            if len(gudongs) == 0 or len(chigubilis) == 0 or gudongs[0] == '' or chigubilis[0] == '':
                print("未知原因缺失:", href['company_name'], href['url'])
                self.unable_5.append(href)
                continue
            else:
                GuDongInfo['企业名称'] = [href['company_name']] * total_len
                GuDongInfo['股东(发起人)'] = gudongs
                GuDongInfo['持股比例'] = chigubilis
                GuDongInfo.to_csv("res/Holder/result.csv", mode='a', header=False, index=True)
                sign = 99

        with open("res/Holder/unable_2.txt", "a") as f:
            for item in self.unable_2:
                f.write(item)
                f.write('\n')
            f.close()

        with open("res/Holder/unable_4.txt", 'w') as f:
            for item in self.unable_4:
                f.write(str(item))
                f.write('\n')
            f.close()

        if raw_sign == 0 or raw_sign == 2:
            with open("res/Holder/unable_5.txt", 'w') as f:
                for item in self.unable_5:
                    f.write(str(item))
                    f.write('\n')
                f.close()
        else:
            with open("res/Holder/unable_5.txt", 'a') as f:
                for item in self.unable_5:
                    f.write(str(item))
                    f.write('\n')
                f.close()

    def DealTimeOut(self):
        print("\n处理超时文件")
        deal = []
        with open("res/Holder/unable_4.txt", "r") as f:
            data = f.read().strip().split('\n')
            print(data)
            for item in data:
                if not item == '':
                    deal.append(eval(item))
            f.close()

        self.run(deal, 1, self.DealTimeOut_times)

        if len(self.unable_4):
            if self.DealTimeOut_times <= 5:
                self.DealTimeOut_times += 1
                self.DealTimeOut()
            else:
                with open("res/Holder/unable_4_remain.txt", "a") as f:
                    for item in deal:
                        f.write(str(item))
                        f.write('\n')
                    f.close()

    def DealUnKnown(self):
        print("\n处理未知原因空缺")
        deal = []
        with open("res/Holder/unable_5.txt", "r") as f:
            data = f.read().strip().split('\n')
            for item in data:
                if not item == '':
                    deal.append(eval(item))
            f.close()

        self.run(deal, 2, self.DealUnKnown_times + 1)

        if len(self.unable_5):
            if self.DealUnKnown_times <= 5:
                self.DealUnKnown_times += 1
                self.DealUnKnown()
            else:
                with open("res/Holder/unable_5_remain.txt", "a") as f:
                    for item in deal:
                        f.write(str(item))
                        f.write('\n')
                    f.close()


if __name__ == '__main__':
    g = GetHolderInfo(begin, end)
    g.run(g.hrefs, 0, 0.1)
    g.DealTimeOut()
    g.DealUnKnown()
    pass
