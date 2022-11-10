# CrawlerBySelenium
基于Selenium爬取天眼查数据


### 运行须知

下载后解压，安装必要的包，运行py文件即可

### 注意事项:

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

  网址匹配后控制台输出匹配成功个数，同时将无法匹配的企业名写入res/unable_1.txt中，将经营状况异常企业名写入res/unable_3.txt
  
  网址匹配所有结果整合写入res/url_info.csv，状态一列0代表正常，1代表经营状况异常，2代表未找到
  
  爬取信息时，会出现无股东信息的情况，写入res/unable_2.txt中

  对于提示超时未获取的企业：该提示完全取决于网络状况，网好可能一次都不会出现，会写入res/unable_4.txt中，执行函数DealTimeOut()可以对该文件中的企业进行重新获取

  对于未知原因信息缺失的企业：原因未知，偶尔会出现，会写入res/unable_5.txt中，执行函数DealUnKnown()可以处理
  
  最后的结果保存在res/result.txt中
  
