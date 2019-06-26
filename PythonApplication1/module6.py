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

num_sql = "SELECT count(*) FROM leetcodespyder.TAG;"
num_results = get_results(num_sql)
all_num = get_num(num_results)

tag_list = []
num_list = []
name_list = []

select_sql = "SELECT * FROM TAG" 
tag_results = get_results(select_sql)
for row in tag_results:

    num = get_num(get_results("SELECT count(*) FROM leetcodespyder.similar where SIM_ID = " + str(row[0])))
    numbi = num / all_num
    if num >  8 :
        tag = []
        tag.append(num)
        if row[3] != 'None':
            tag.append(row[1]+ "-"+ row[3]+ " "+ str(round(numbi, 3)))
        else :
            tag.append(row[1]+ " "+ str(round(numbi, 3)))
        tag_list.append(tag)



tag_list.sort(reverse = True)
print(tag_list)


for tag in tag_list :
    name_list.append(tag[1])
    num_list.append(tag[0])

# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['font.family']='sans-serif'
# plt.bar(name_list,num_list)

# ax = plt.gca()

# ax.set_xticklabels( name_list,rotation=45,ha='right')
# plt.tight_layout()

# plt.title("TAG分类情况")
# plt.show()

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family']='sans-serif'

labels=name_list
sizes= num_list
plt.pie(sizes,labels=labels,shadow=False,startangle=90)
plt.axis('equal')
plt.title("主流算法类型占比")
plt.show()

