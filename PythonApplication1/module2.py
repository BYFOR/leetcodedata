#添加问题题干、通过数、提交数、建立相似问题关系数据
import pymysql
import http.cookiejar as cookielib
import urllib.request
import requests
import json
#import datetime

#初始化可获取问题列表
question_list = []

# 打开数据库连接
db = pymysql.connect("localhost","root","123456","leetcodespyder" )
 
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
# question_sql 查询语句获取非付费问题列表
question_sql = "SELECT QUESTION_ID, TITLESLUG FROM QUESTION WHERE PAID != \"True\" " 
try:
   # 执行question_sql语句
   cursor.execute(question_sql)
   # 获取所有记录列表
   results = cursor.fetchall()
   for row in results:
      #问题信息列表
      question = []
      question.append(row[0])
      question.append(row[1])
      #问题列表
      question_list.append(question)
   print("\033[1;32;40m非付费问题列表请求成功!\033[0m")
except:
   print("\033[1;31;40m非付费问题列表请求失败!\033[0m")



#print(question_list)

#请求头信息
url="https://leetcode-cn.com/graphql"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
payloadData = {"operationName":"questionData","variables":{"titleSlug":"two-sum"},"query":"query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    __typename\n  }\n}\n"}

#开始循环遍历请求题目详细信息
for question in question_list:
   print("开始请求获取问题：", question[1], "问题编号：",question[0])

   #设定请求标题
   payloadData["variables"]["titleSlug"] = question[1]
   
   #请求数据
   question_data = requests.post(url, json=payloadData, headers=headers)
   questions_json = json.loads(question_data.text)
   #print(questions_json)

   #输出题目信息
   #print(questions_json["data"]["question"]["translatedTitle"])
   # print(questions_json["data"]["question"]["content"])
   # print(questions_json["data"]["question"]["translatedContent"])
   # print(json.loads(questions_json["data"]["question"]["stats"])["totalAcceptedRaw"])
   # print(json.loads(questions_json["data"]["question"]["stats"])["totalSubmissionRaw"])
   if questions_json["data"]["question"]["titleSlug"] ==  question[1] :
      print("请求成功")
   #生成信息插入SQL语句
   question_sql = "UPDATE question SET " 
   question_sql = question_sql + "CONTENT="+ "\""+ str(questions_json["data"]["question"]["content"])+ '\", '
   question_sql = question_sql + "TRANSLATEDTITLE="+ "\""+  str(questions_json["data"]["question"]["translatedTitle"])+ '\", '
   question_sql = question_sql + "TEANSLATEDCONTENT="+ "\""+ str(questions_json["data"]["question"]["translatedContent"])+ '\", '
   question_sql = question_sql +  "ACCEPT="+ str(json.loads(questions_json["data"]["question"]["stats"])["totalAcceptedRaw"])+ ', '
   question_sql = question_sql +  "SUBMISSION="+ str(json.loads(questions_json["data"]["question"]["stats"])["totalSubmissionRaw"])+ ' '
   question_sql = question_sql +  "WHERE QUESTION_ID="+str(question[0])
   #print ("信息更新SQL语句：", question_sql)
   try:
      # 执行sql语句
      cursor.execute(question_sql)
      # 提交到数据库执行
      db.commit()
      print("question更新","\033[1;32;40mSUCCESS!\033[0m")
   except:
      # 如果发生错误则回滚
      db.rollback()
      print("question更新","\033[1;31;40mERROR!\033[0m")


   #抽取相似问题列表   
   similar_questions = json.loads(questions_json["data"]["question"]["similarQuestions"])
   for i in similar_questions:
      #根据相似问题请求标题获取该问题ID
      select_sql = "select QUESTION_ID from question where TITLESLUG = "+ "\""+ i["titleSlug"]+ "\""
      #print("select_sql:",select_sql)
      try:
         # 执行question_sql语句
         cursor.execute(select_sql)
         # 获取所有记录列表
         results = cursor.fetchall()
         print("\033[1;32;40mselect_SUCCESS!\033[0m")
         for row in results:
            similar_question = []
            similar_question.append(row[0])
            #print(row[0])
            for j in similar_question :
               similar_sql = "INSERT INTO SIMILAR(QUE_ID,SIM_ID) VALUES ("
               similar_sql = similar_sql + str(question[0]) +", "
               similar_sql = similar_sql + str(j) +")"
               #print ("相似题目插入SQL语句：", similar_sql)
               try:
                  # 执行sql语句
                  cursor.execute(similar_sql)
                  # 提交到数据库执行
                  db.commit()
                  print("question插入","\033[1;32;40mSUCCESS!!\033[0m")
               except:
                  # 如果发生错误则回滚
                  db.rollback()
                  print("similar插入","\033[1;31;40mERROR!!\033[0m")
      except:
         # 如果发生错误则回滚
         db.rollback()
         print("\033[1;31;40mselect_ERROR!\033[0m")
   print("QUESTION_ID:",question[0],"\033[1;32;40m请求完毕!!!!!\033[0m")

# 关闭数据库连接
db.close()

print("爬取结束！")
