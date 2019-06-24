#爬取Leetcode题目列表获得QUESTION_ID（题目ID）、TITLE（标题）、TITLESLUG（请求标题）、DIFFICULTY（难度等级）、FRONTEND（前端ID）、PAID（是否付费题目）

import http.cookiejar as cookielib
import urllib.request
import requests
import json
import datetime
import pymysql

#开始请求问题列表
url="https://leetcode-cn.com/api/problems/all/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
questions = requests.get(url, headers=headers)

#格式化请求内容为JSON
questions_json = json.loads(questions.text)

#抽取问题列表
questions_list = questions_json['stat_status_pairs']


# 打开数据库连接
db = pymysql.connect("localhost","root","123456","leetcodespyder" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

#循环遍历题目信息
for question_info in questions_list:
    # print(question_info['stat']['question_id'])
    # print(question_info['stat']['question__title'])
    # print(question_info['stat']['question__title_slug'])
    # print(question_info['difficulty']['level'])
    # print(question_info['paid_only'])
    # print(question_info['stat']['frontend_question_id'])

    # SQL 插入语句
    sql = "INSERT INTO question(QUESTION_ID,TITLE,TITLESLUG,DIFFICULTY,PAID,FRONTEND) VALUES ("
    sql = sql + str(question_info['stat']['question_id'])+', '
    sql = sql + "\'"+ question_info['stat']['question__title']+ "\', "
    sql = sql + "\'"+ question_info['stat']['question__title_slug']+ "\', "
    sql = sql + str(question_info['difficulty']['level'])+ ", "
    sql = sql + "\'"+ str(question_info['paid_only'])+ "\', "
    sql = sql + str(question_info['stat']['frontend_question_id'])+ ")"
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print("QUESTION_ID:",question_info['stat']['question_id'],"\033[1;32;40mSUCCESS!\033[0m")
    except:
        # 如果发生错误则回滚
        db.rollback()
        print("QUESTION_ID:",question_info['stat']['question_id'],"\033[1;31;40mERROR!\033[0m")

# 关闭数据库连接
db.close()