import random
import pymysql
import matplotlib.pyplot as plt
import pygal
import numpy as np
def get_results( sql ) :
    # 打开数据库连接
    db = pymysql.connect("localhost","root","123456","leetcodespyder" )
    
    # 使用cursor()方法获取操作游标 
    cursor = db.cursor()
    select_data_list = []
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print ("Error: unable to fetch data")
def get_num (results) :
    return results[0][0]

num_sql = "SELECT count(*) FROM SOLUTION;"
num_results = get_results(num_sql)
all_num = get_num(num_results)

language_list = []
num_list = []
name_list = []

select_sql = "SELECT * FROM LANGUAGE" 
language_results = get_results(select_sql)
for row in language_results:
    language = []
    num = get_num(get_results("SELECT count(*) FROM solution where LANGUAGE_ID = " + str(row[0]))) / all_num
    if num != 0.0 :
        language.append(num)
        language.append(row[1])
        language_list.append(language)

language_list.sort(reverse = True)

for i in language_list :
    print ( i )

for language in language_list :
    name_list.append(language[1])
    num_list.append(language[0])

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family']='sans-serif'

labels=name_list
sizes= num_list
plt.pie(sizes,labels=labels,shadow=False,startangle=90)
plt.axis('equal')
plt.title("耗时小于100ms的题解中主流语言分布情况")
plt.show()