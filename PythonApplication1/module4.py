#建立IP代理池，对题解按语言和耗时进行爬取，暴力遍历题解的APIURL实现
from bs4 import BeautifulSoup
import subprocess as sp
from lxml import etree
import requests
import random
import re
import pymysql
import http.cookiejar as cookielib
import urllib.request
import json
import time


#从GITHUB https://github.com/jhao104/proxy_pool 测试服务器获取代理IP
def get_proxy():
    proxies = {'http': ''}
    proxy = requests.get("http://118.24.52.95:5010/get/").content.decode()
    proxies["http"] = proxy
    return proxies

# 函数说明:获取IP代理
# Parameters:
#     page - 高匿代理页数,默认获取第一页
# Returns:
#     proxys_list - 代理列表

def get_proxys( ):
    #requests的Session可以自动保持cookie,不需要自己维护cookie内容
    S = requests.Session()
    for page in range(3):
        #存储代理的列表
        proxys_list = []
        #西祠代理高匿IP地址
        pageurl = page + 1
        target_url = 'http://www.xicidaili.com/nn/%d' % pageurl
        #完善的headers
        target_headers = {'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer':'http://www.xicidaili.com/nn/',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
        }
        #get请求
        target_response = S.get(url = target_url, headers = target_headers)
        #utf-8编码
        target_response.encoding = 'utf-8'
        #获取网页信息
        target_html = target_response.text
        #获取id为ip_list的table
        bf1_ip_list = BeautifulSoup(target_html, 'lxml')
        bf2_ip_list = BeautifulSoup(str(bf1_ip_list.find_all(id = 'ip_list')), 'lxml')
        ip_list_info = bf2_ip_list.table.contents
        #存储代理的列表
        proxys = []
        #爬取每个代理信息
        for index in range(len(ip_list_info)):
            if index % 2 == 1 and index != 1:
                dom = etree.HTML(str(ip_list_info[index]))
                ip = dom.xpath('//td[2]')
                port = dom.xpath('//td[3]')
                protocol = dom.xpath('//td[6]')
                proxys_list.append(protocol[0].text.lower() + '#' + ip[0].text + '#' + port[0].text)
        #返回代理列表
        proxys_list = proxys_list + proxys
    return proxys_list


# 函数说明:检查代理IP的连通性
# Parameters:
#     ip - 代理的ip地址
#     lose_time - 匹配丢包数
#     waste_time - 匹配平均时间
# Returns:
#     average_time - 代理ip平均耗时

def check_ip(ip, lose_time, waste_time):
    #命令 -n 要发送的回显请求数 -w 等待每次回复的超时时间(毫秒)
    cmd = "ping -n 3 -w 3 %s"
    #执行命令
    p = sp.Popen(cmd % ip, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    #获得返回结果并解码
    out = p.stdout.read().decode("gbk")
    #丢包数
    lose_time = lose_time.findall(out)
    #当匹配到丢失包信息失败,默认为三次请求全部丢包,丢包数lose赋值为3
    if len(lose_time) == 0:
        lose = 3
    else:
        lose = int(lose_time[0])
    #如果丢包数目大于2个,则认为连接超时,返回平均耗时1000ms
    if lose > 2:
        #返回False
        return 1000
    #如果丢包数目小于等于2个,获取平均耗时的时间
    else:
        #平均时间
        average = waste_time.findall(out)
        #当匹配耗时时间信息失败,默认三次请求严重超时,返回平均好使1000ms
        if len(average) == 0:
            return 1000
        else:
            #
            average_time = int(average[0])
            #返回平均耗时
            return average_time

# 函数说明:初始化正则表达式
# Parameters:
#     无
# Returns:
#     lose_time - 匹配丢包数
#     waste_time - 匹配平均时间

def initpattern():
    #匹配丢包数
    lose_time = re.compile(u"丢失 = (\d+)", re.IGNORECASE)
    #匹配平均时间
    waste_time = re.compile(u"平均 = (\d+)ms", re.IGNORECASE)
    return lose_time, waste_time


#从 https://www.xicidaili.com/ 获取代理IP
def get_ip() :
    #初始化正则表达式
    lose_time, waste_time = initpattern()
    #获取IP代理
    proxys_list = get_proxys()

    #如果平均时间超过200ms重新选取ip
    while True:
        #从100个IP中随机选取一个IP作为代理进行访问
        proxy = random.choice(proxys_list)
        split_proxy = proxy.split('#')
        #获取IP
        ip = split_proxy[1]
        #检查ip
        average_time = check_ip(ip, lose_time, waste_time)
        if average_time > 200:
            #去掉不能使用的IP
            proxys_list.remove(proxy)
            print("ip连接超时, 重新获取中!")
        if average_time < 200:
            break
    #去掉已经使用的IP
    proxys_list.remove(proxy)
    proxy_dict = {split_proxy[0]:split_proxy[1] + ':' + split_proxy[2]}
    print("使用代理:", proxy_dict)
    return proxy_dict



# 打开数据库连接
db = pymysql.connect("localhost","root","123456","leetcodespyder" )
 
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
select_id_list = []
select_language_list = []
# SQL 查询语句
select_id_sql = "SELECT QUESTION_ID FROM QUESTION WHERE PAID != \"True\" " 
try:
    # 执行SQL语句
    cursor.execute(select_id_sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        select_id = row[0]
        select_id_list.append(select_id)
except:
    print ("Error: unable to fetch data")
print(len(select_id_list))

#获得程序语言信息，数据量过大只选定主流语言
select_language_list = [['cpp', 1], ['java', 2], ['python', 3], ['python3', 4], ['c', 8], ['csharp', 9]]

#请求头信息
headers = {'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding':'gzip, deflate, sdch, br','Accept-Language':'zh-CN,zh;q=0.8',}
cookies = {'cookie': 'YOUR cookies'}

#获取设定代理节点
#proxies = {'http': ''}
# proxy = get_proxy().decode()
# proxies["http"] = proxy
proxies = get_ip()
print("\033[1;34;40m",proxies,"\033[0m")

#有效solution计数
nums = 0

for id in select_id_list:   #问题循环
    for language in select_language_list:   #语言循环
        for tim in range(100):  #耗时循环
            time_start=time.time()  #开始计时
            solution_url = "https://leetcode-cn.com/submissions/api/detail/"+str(id)+"/"+str(language[0])+"/"+str(tim+1)+"/"
            print(solution_url)
            solution_res = requests.get(solution_url, headers=headers, cookies=cookies, proxies=proxies) 
            tmp = 1 #请求标记值
            while tmp == 1:
                print("solution_url:",solution_url,"       num:",nums)

                #429 错误，更换代理，重新请求，直到请求成功
                if solution_res.status_code == 429 :
                    print("\033[1;32;40m",solution_res.status_code,"\033[0m")
                    proxies = get_ip()
                    # proxy = get_proxy().decode()
                    # proxies["http"] = proxy
                    solution_res = requests.get(solution_url, headers=headers, cookies=cookies, proxies=proxies)
                    print("\033[1;34;40m",proxies,"\033[0m")

                #200 请求成功，获得solution
                elif solution_res.status_code == 200:
                    print("\033[1;32;40m",solution_res.status_code,"\033[0m")
                    solution_json = json.loads(solution_res.text)
                    solution_sql = "INSERT INTO solution(QUESTION_ID,LANGUAGE_ID,TIME,QUE_SOLUTION) VALUES ("
                    solution_sql = solution_sql + str(id)+', '
                    solution_sql = solution_sql + str(language[1])+ ", "
                    solution_sql = solution_sql + str(tim+1)+ ", "
                    solution_sql = solution_sql + "\'"+ str(solution_json["code"])+ "\')"
                    print("solution_sql:",solution_sql)
                    try:
                        # 执行sql语句
                        cursor.execute(solution_sql)
                        # 提交到数据库执行
                        db.commit()
                        print("\033[1;32;40mSUCCESS!\033[0m")
                        nums = nums + 1
                    except:
                        # 如果发生错误则回滚
                        db.rollback()
                        print("\033[1;31;40mERROR!      ERROR!      ERROR!\033[0m")
                    break
                #其状态码，出错跳过
                else :
                    print("\033[1;31;40m",solution_res.status_code,"\033[0m")
                    break
            #计算输出该solution用时
            time_end=time.time()
            print('                                                                              TIME COST:',time_end-time_start)
# 关闭数据库连接
db.close()
#输出有效solution数
print(nums)