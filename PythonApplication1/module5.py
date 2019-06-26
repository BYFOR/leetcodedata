# !pip install brewer2mpl
#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import warnings; warnings.filterwarnings(action='once')
import random
import pymysql
import json
import time


large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")

# 打开数据库连接
db = pymysql.connect("localhost","root","123456","leetcodespyder" )
 
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
select_data_list = []
# SQL 查询语句
select_id_sql = "SELECT DIFFICULTY, ACCEPT, SUBMISSION, SOLUTION_NUM FROM QUESTION WHERE PAID != \"True\" " 
try:
    # 执行SQL语句
    cursor.execute(select_id_sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        data = []
        data.append(row[0])
        data.append(row[1]/row[2])
        data.append(row[3])
        select_data_list.append(data)
except:
    print ("Error: unable to fetch data")
# print(select_data_list)
data_pd = pd.DataFrame(select_data_list,columns=['DIFFICULTY','ACCEPT/SUBMISSION', 'SOLUTION_NUM'],dtype=float)
#print(df)



#去重
SOLUTION_NUM = np.unique(data_pd['SOLUTION_NUM'])
colors = [plt.cm.tab10(i/float(len(SOLUTION_NUM)-1)) for i in range(len(SOLUTION_NUM))]

plt.figure(figsize=(16, 10), dpi= 80, facecolor='w', edgecolor='k')

for i, SOLUTION_NUM in enumerate(SOLUTION_NUM):
    plt.scatter('ACCEPT/SUBMISSION', 'SOLUTION_NUM', data=data_pd.loc[data_pd.SOLUTION_NUM==SOLUTION_NUM, :], s=20, cmap=colors[i], label=str(SOLUTION_NUM))

plt.gca().set(xlim=(0.0, 1), ylim=(0, 60), xlabel='ACCEPT/SUBMISSION', ylabel='DIFFICULTY')

plt.xticks(fontsize=12); plt.yticks(fontsize=12)
plt.title("ACCEPT/SUBMISSION with DIFFICULTY", fontsize=22)
plt.legend(fontsize=12)    
plt.show()