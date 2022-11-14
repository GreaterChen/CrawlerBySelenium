# CrawlerBySelenium
基于Selenium爬取天眼查数据

### 爬取内容
1.所有企业对应的网址
2.股东信息的股东、持股比例
3.对外投资的被投资企业、投资比例
4.待完成

### 运行须知

1.下载后解压，安装必要的包

2.在正式开始爬取前，务必先删除res/url/url_info_total.csv,随后务必运行init.py

3.先运行GetURL.py获取网址信息，每次爬取更改begin、end值以确定索引范围为左闭右开的[begin,end),tips:索引从0开始

4.在获取URL后可同步运行GetHolder.py 和 GetInverst.py,分别获取股东信息和对外投资信息。每次爬取更改begin、end值

### 注意事项:
  在Crawler.py中：

  该行为服务器配置需要：

  self.browser = webdriver.Chrome(options=option, executable_path='/root/chromedriver')

  本地使用需注释此行并取消注释：

  self.browser = webdriver.Chrome(chrome_options=option)
  
  将该行注释可以在运行时弹出chrome浏览器进行监控，服务器运行必须取消注释

  option.add_argument("headless")

### 网址匹配：

  搜索关键词，先看搜索结果第一项是否匹配，若匹配，搜索企业经营状况，若正常则匹配成功，若异常则匹配结束---1
  
  若不匹配，则考虑将匹配'有限公司'改为匹配‘有限责任公司’(由数据集发现的通性问题),若匹配，搜索企业经营状况，若正常则匹配成功，若异常则匹配结束---2
  
  若不匹配，考虑查询的企业名字完全包含xlsx企业名称的情况，比如河北省xxx公司匹配xxx公司，若匹配，搜索企业经营状况，若正常则匹配成功，若异常则匹配结束---3

  若不匹配，考虑查询企业名字去除括号的结果，若匹配，搜索企业经营状况，若正常则匹配成功，若异常则匹配结束---4
  
  若不匹配，查询界面中第一个"历史名称"字段，看跟着的名字是否匹配，重复2、3、4---5
  
  若不匹配，将xxx有限公司改为xxx有限责任公司重新查询，重复2、3、4、5---6
  
  tips:刚开始的几个含英文字母的公司匹配的不太好，但也只有那几个含英文字母的公司，人工处理即可。
  
### 结果保存：

  网址匹配后控制台输出匹配成功个数，同时将无法匹配的企业名写入res/url/unable_1.txt中，将经营状况异常企业名写入res/url/unable_3.txt
  
  网址匹配所有结果整合写入res/url/url_info.csv，状态一列0代表正常，1代表经营状况异常，2代表未找到
  
  爬取股东信息时，会出现无股东信息的情况，写入res/Holder/unable_2.txt中

  对于提示超时未获取的企业：该提示取决于网络状况,程序会执行最多五次DealTimeOut()对该文件中的企业进行重新获取，仍未获取的写入res/Holder/unable_4.remain.txt中

  对于未知原因信息缺失的企业：原因未知，偶尔会出现，程序会执行最多五次DealUnKnown()对该文件中的企业进行重新获取，仍未获取的写入res/Holder/unable_5.remain.txt中
  
  最后的结果保存在res/Holder/result.txt中

  爬取对外投资和爬取股东信息类似，相关文件存储于res/Inverst中
  
