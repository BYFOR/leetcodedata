#添加tags，并将问题按tag分类建立class关系表

import http.cookiejar as cookielib
import urllib.request
import requests
import json
import datetime
import pymysql


# 打开数据库连接
db = pymysql.connect("localhost","root","123456","leetcodespyder" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

#开始请求问题列表
url="https://leetcode-cn.com/problems/api/tags/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
questions = requests.get(url, headers=headers)

#格式化请求内容为JSON
tags_json = json.loads(questions.text)
tags_list = tags_json["topics"]
i=1

for tag in tags_list:
    # SQL 插入语句
    tag_sql = "INSERT INTO tag(TAG_ID,NAME,TAGSLUG,TRANSLATEDNAME) VALUES ("
    tag_sql = tag_sql + str(i)+', '
    tag_sql = tag_sql + "\'"+ str(tag['name'])+ "\', "
    tag_sql = tag_sql + "\'"+ str(tag['slug'])+ "\', "
    tag_sql = tag_sql + "\'"+ str(tag['translatedName'])+ "\')"
    print("tag_sql:",tag_sql)
    try:
        # 执行sql语句
        cursor.execute(tag_sql)
        # 提交到数据库执行
        db.commit()
        print("\033[1;32;40mCLASSSUCCESS!\033[0m")
    except:
        # 如果发生错误则回滚
        db.rollback()
        #print("\033[1;31;40mCLASSERROR!\033[0m")
    
    for j in tag["questions"] :
        class_sql = "INSERT INTO class(TAG_ID,QUESTION_ID) VALUES ("
        class_sql = class_sql + str(i)+ ", "
        class_sql = class_sql + str(j)+ ")"
        print("class_sql:",class_sql)
        try:
            # 执行sql语句
            cursor.execute(class_sql)
            # 提交到数据库执行
            db.commit()
            #print("\033[1;32;40mCLASSSUCCESS!\033[0m")
        except:
            # 如果发生错误则回滚
            db.rollback()
            print("\033[1;31;40mCLASSERROR!\033[0m")
    i = i + 1
db.close()