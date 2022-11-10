# CrawlerBySelenium
基于Selenium爬取天眼查数据


下载后解压，运行py文件即可

### 网址匹配：

  搜索关键词，先看搜索结果第一项是否匹配，
  
  若不匹配，则考虑将匹配'有限公司'改为匹配‘有限责任公司’(由数据集发现的通性问题),
  
  若不匹配，考虑查询的企业名字完全包含xlsx企业名称的情况，比如河北省xxx公司匹配xxx公司(感觉不能100%保证就是那家,若十分追求准确性建议删除)
  
  若不匹配，查询界面中第一个"历史名称"字段，看跟着的名字是否匹配
  
  若不匹配，将xxx有限公司改为xxx有限责任公司重新查询
  
  tips:刚开始的几个含英文名的公司匹配的不太好，但也只有那几个含英文公司，人工筛选即可
  
  前200个数据在不包含上述含英文公司的情况下可以匹配到197个
  
### 结果保存：

  网址匹配后控制台输出匹配成功个数，同时将无法匹配的企业名写入res/unable_1.txt中
  
  爬取股信息时，会出现无股东信息的情况，该类公司每发现五个便写入一次res/unable_2.txt中
  
  但注意该文件（只有该文件会）每次运行都会被清除，多次分段爬虫记得改文件名
  
  最后的结果保存在res/result.txt中
  
