import pandas as pd
# if os.path.isfile("res/url/url_info_total.csv"):
#     os.remove("res/url/url_info_total.csv")

# 若不存在则创建、若存在则清空内容
# URL
open("res/url/unable_1.txt", "w").truncate()
open("res/url/unable_3.txt", "w").truncate()

# Holder
open("res/Holder/result.csv", "w").truncate()
temp = pd.DataFrame()
temp['企业名称'] = []
temp['股东(发起人)'] = []
temp['持股比例'] = []
temp.to_csv("res/Holder/result.csv")

open("res/Holder/unable_2.txt", "w").truncate()

# Inverst
open("res/Inverst/result.csv","w").truncate()
temp = pd.DataFrame()
temp['企业名称'] = []
temp['被投资企业名称'] = []
temp['投资比例'] = []
temp.to_csv("res/Inverst/result.csv")

open("res/Inverst/unable_2.txt","w").truncate()

