import pandas as pd

from Crawler import *

begin = 60000
end = 70000


class GetInverst(Crawler):
    def __init__(self, begin, end):
        super(GetInverst, self).__init__()
        url_info = pd.read_csv('res/url/url_info_total.csv')
        name = url_info[url_info['网址'] != '-']['企业名称'].to_list()
        url = url_info[url_info['网址'] != '-']['网址'].to_list()
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

        for href in tqdm(hrefs, desc='获取信息', file=sys.stdout):
            self.browser.get(href['url'])
            InverstInfo = pd.DataFrame()
            try:
                Inverst_title = self.browser.find_element_by_xpath(
                    '//div[@class="index_tag-nav-root__DyEBq"]/a[contains(text(),"对外投资")]')
                if Inverst_title.text[:4] != '对外投资':  # 可能会匹配到'历史对外投资'
                    print("无对外投资信息:", href['company_name'], href['url'])
                    self.unable_2.append(href['company_name'])
                    continue
                total_len = int(Inverst_title.find_element_by_xpath("./span").text)
            except:
                print("无对外投资信息:", href['company_name'], href['url'])
                self.unable_2.append(href['company_name'])
                continue

            Inversts = []
            Ratio = []

            page = int((total_len - 1) / 10) + 1
            current_page = 0

            try:
                while page != current_page:
                    if current_page == 1:
                        temp = self.browser.find_element_by_id("inverst-table")
                        footer = temp.find_element_by_xpath(
                            f"./div/div[@class='table-footer']/div/div/div/div[{page + 1}]/i")
                        self.browser.execute_script("arguments[0].click();", footer)
                    elif current_page > 1:
                        temp = self.browser.find_element_by_id("inverst-table")
                        footer = temp.find_element_by_xpath(
                            f"./div/div[@class='table-footer']/div/div/div/div[{page + 2}]/i")
                        self.browser.execute_script("arguments[0].click();", footer)
                    sleep(sleep_time)
                    WebDriverWait(self.browser, 2).until(
                        lambda diver: self.browser.find_element_by_id("inverst-table"))
                    Inverst = self.browser.find_element_by_id("inverst-table")
                    Inverst = Inverst.find_elements_by_xpath("./div/table/tbody/tr")
                    for item in Inverst:
                        WebDriverWait(self.browser, 10)
                        data = item.find_elements_by_xpath("./td")
                        try:
                            WebDriverWait(self.browser, 2).until(
                                lambda diver: data[1].find_element_by_xpath("./div/div[2]/div/div/a"))
                        except:
                            total_len -= 1
                            continue
                        status = data[6].text
                        if '存续' in status or '在营' in status or '开业' in status or '在册' in status:
                            Inversts.append(data[1].find_element_by_xpath("./div/div[2]/div/div/a").text)
                            Ratio.append(data[5].text)
                        else:
                            total_len -= 1
                    current_page += 1
            except:
                print("超时未获取：", href['company_name'], href['url'])
                self.unable_4.append(href)
                continue

            InverstInfo = pd.DataFrame()
            InverstInfo['企业名称'] = [href['company_name']] * len(Inversts)
            InverstInfo['被投资企业名称'] = Inversts
            InverstInfo['投资比例'] = Ratio
            InverstInfo.to_csv("res/Inverst/result.csv", mode='a', header=False, index=True)
            sign = 99

        with open("res/Inverst/unable_2.txt", "a") as f:
            for item in self.unable_2:
                f.write(item)
                f.write('\n')
            f.close()

        with open("res/Inverst/unable_4.txt", "w") as f:
            for item in self.unable_4:
                f.write(str(item))
                f.write('\n')
            f.close()

        if raw_sign == 0 or raw_sign == 2:  # 如果第一次经过或在处理异常未获取
            with open("res/Inverst/unable_5.txt", "w") as f:
                for item in self.unable_5:
                    f.write(str(item))
                    f.write('\n')
                f.close()
        else:  # raw_sign == 1,在处理超时
            with open("res/Inverst/unable_5.txt", "a") as f:
                for item in self.unable_5:
                    f.write(str(item))
                    f.write('\n')
                f.close()

    def DealTimeOut(self):
        print("\n处理超时文件")
        deal = []
        with open("res/Inverst/unable_4.txt", "r") as f:
            data = f.read().strip().split('\n')
            print(data)
            for item in data:
                if not item == '':
                    deal.append(eval(item))
            f.close()

        self.run(deal, 1, self.DealTimeOut_times*0.2 + 0.4)

        if len(self.unable_4):
            if self.DealTimeOut_times <= 5:
                self.DealTimeOut_times += 1
                self.DealTimeOut()
            else:
                with open("res/Inverst/unable_4_remain.txt", "a") as f:
                    for item in deal:
                        f.write(str(item))
                        f.write('\n')
                    f.close()

    def DealUnKnown(self):
        print("\n处理未知原因空缺")
        deal = []
        with open("res/Inverst/unable_5.txt", "r") as f:
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
                with open("res/Inverst/unable_5_remain.txt", "a") as f:
                    for item in deal:
                        f.write(str(item))
                        f.write('\n')
                    f.close()


if __name__ == '__main__':
    g = GetInverst(begin, end)
    g.run(g.hrefs, 0, 0.2)
    g.DealTimeOut()
    g.DealUnKnown()
