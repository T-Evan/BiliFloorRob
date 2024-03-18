# -*- coding: utf-8 -*-
"""
Created on 2017-08-17
Update on 2018-05-12
@author: yiwan
"""

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import time
import re
import requests
import random
from multiprocessing.dummy import Pool as ThreadPool
from requests.adapters import HTTPAdapter

pro = ['118.190.210.227:3128', '114.113.126.82:80', '120.79.133.2128088']


def read_cookie(cookiepath):
    with open(cookiepath, 'r') as fid:
        cookies = fid.readlines()
    return cookies


class BILI(object):
    def __init__(self, Cookie, csrf, pushPlusToken, serverPushToken):
        self.s = requests.Session()
        self.Cookie = Cookie
        self.csrf = csrf
        self.pushPlusToken = pushPlusToken
        self.serverPushToken = serverPushToken
        # 重试
        request_retry = HTTPAdapter(max_retries=3)
        self.s.mount('http://', request_retry)

    def get_comment(self, av_num, desc_type):
        header = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': self.Cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Host': 'api.bilibili.com'
        }
        reply_type = desc_type
        try:
            r = self.s.get(
                'http://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=' + str(reply_type) + '&sort=0&oid=' + str(av_num),
                headers=header)
            replies = r.json()['code']
            if replies == 0:  # 继续判断是否为转发动态
                return 
            else:
                return "get_comment unkown desc_type"
        except Exception as e:
            print(e)
            print(r)
            # exit()

    def get_dynamic(self, av_num, desc_type):
        header = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': self.Cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Host': 'api.bilibili.com'
        }
        reply_type = desc_type
        try:
            r = self.s.get(
                'https://api.bilibili.com/x/polymer/web-dynamic/v1/detail&id=' + str(av_num),
                headers=header)
            replies = r.json()['code']
            if replies == 0:  # 继续判断是否为转发动态
                upName = r.json()['data']['items'][0]['modules']['module_author']['name']
                avType = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['badge']['text']
                avTitle = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['title']
                avDesc = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['desc']
                return upName, avType, avTitle, avDesc
            else:
                return "get_comment unkown desc_type"
        except Exception as e:
            print(e)
            print(r)
            # exit()

    def get_comment_num(self, av_num, desc_type):
        header = {
            'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': self.Cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Host': 'api.bilibili.com'
        }
        reply_type = desc_type
        try:
            uri = 'http://api.bilibili.com/x/v2/reply/count?jsonp=jsonp&type=' + str(reply_type) + '&oid=' + av_num
            r = self.s.get(
                uri,
                headers=header)
            replies = r.json()['code']
            if replies == 0:  # 继续判断是否为转发动态
                if r.json()['data']['count'] >= 0:
                    return (r.json()['data']['count'], reply_type)
                else:
                    return 0, reply_type
            else:
                return "get_comment_num unkown desc_type"
        except Exception as e:
            print(e)
            print(r)
            print(r.raw)
            print(uri)
            # exit()

    def send_comment(self, av_num, message, reply_type, upName, avType, avTitle, avDesc):
        header = {
            'Accept': 'application/json, text/plain, */*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Content-Length': '106',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': self.Cookie,
            'Host': 'api.bilibili.com',
            'Origin': 'https://t.bilibili.com',
            'Referer': 'https://t.bilibili.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36 '
        }
        # if type == 1:
        #     post_data = {
        #         'jsonp': 'jsonp',
        #         'message': message,
        #         'type': type,
        #         'plat': '1',
        #         'oid': av_num,
        #         'csrf': self.csrf
        #     }
        # elif type == 17 or type == 11:
        #     post_data = {
        #         'jsonp': 'jsonp',
        #         'message': message,
        #         'type': type,
        #         'oid': av_num,
        #         'csrf': self.csrf
        #     }
        # comment_url = "http://api.bilibili.com/x/reply/add"
        post_data = {
                    'jsonp': 'jsonp',
                    'message': message,
                    'type': reply_type,
                    'oid': av_num,
                    'csrf': self.csrf
                }
        comment_url = "https://api.bilibili.com/x/v2/reply/add"

        try:
            r = self.s.post(comment_url, headers=header, data=post_data)
            if r.json()['code'] == 0:
                print('ok')
                pushPlusLink = "http://www.pushplus.plus/send?token=" + self.pushPlusToken  +"&title=bilibili抢楼&content=up主[" + upName + "]" + avType + "[" + avTitle + "]" + "[" + avDesc + "]" + "&template=html"
                r = self.s.get(pushPlusLink)
                serverPushLink = "https://sctapi.ftqq.com/" + self.serverPushToken  +".send?title=bilibili抢楼&desp=up主[" + upName + "]" + avType + "[" + avTitle + "]" + "[" + avDesc + "]"
                r = self.s.get(serverPushLink)
            else:
                print('error')
                print(r.json())
        except Exception as e:
            print(e)
            # exit()

    def get_newest(self):

        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': self.Cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        # 注意type=1时不含番剧信息
        # url = "http://api.bilibili.com/x/feed/pull?jsonp=jsonp&ps=10&type=0"
        # try:
        #     r = self.s.get(url, headers=header)
        #     av_num = r.json()['data']['feeds'][0]['add_id']
        #     return str(av_num)
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?type=video"
        try:
            # r = self.s.get(url, proxies={'http': random.choice(pro)},  headers=header)
            r = self.s.get(url, headers=header)
            desc_type = r.json()['data']['items'][0]['basic']['comment_type']
            upName = r.json()['data']['items'][0]['modules']['module_author']['name']
            avType = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['badge']['text']
            avTitle = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['title']
            avDesc = r.json()['data']['items'][0]['modules']['module_dynamic']['major']['archive']['desc']
            if desc_type == 1 or desc_type == 17 or desc_type == 12 :
                return str(r.json()['data']['items'][0]['basic']['comment_id_str']), desc_type, upName, avType, avTitle, avDesc
            elif desc_type == 11 or desc_type == 19: #1为转发动态，4为纯文字动态，暂时无法获取用于评论的动态id
                return str(r.json()['data']['items'][0]['basic']['comment_id_str']), desc_type, upName, avType, avTitle, avDesc
                # return ("unkown"),desc_type
                av_num = r.json()['data']['items'][0]['card']
                searchObj = re.search(r'(dynamic_id.*\d*)', av_num, re.M | re.I)
                if searchObj:
                    searchObj = re.findall(r'\d+', searchObj.group(1))
                    return str(searchObj[0])
            else:
                return str('error')
        except Exception as e:
            print("getnewtest wrong")
            print(e)
            print(r.json())
            # exit()

    # 快速模式，慢速模式。。
    def run(self, av_num=None, floor=0, content=None, award=False, reply_type=0):
        if content is None:
            # '1楼精准打击～没有人能在我的关注里打败我，大大的flag233'
            content = "多线程~" + str(floor) + '楼精准打击～'
        # 指定抽奖动态盖楼抢楼
        if award is True and av_num is not None:
            while 1:
                topfloor = self.get_comment_num(av_num)
                print(topfloor)
                topfloors1 = [999, 998, 997]
                topfloors2 = [298, 299, 297]
                if topfloor % 1000 in topfloors1 or topfloor % 300 in topfloors2:
                    self.send_comment(av_num, content)
                if 1000 - topfloor % 1000 < 100 or 300 - topfloor % 300 < 100:
                    time.sleep(0.1)
                    continue
                # if 300-topfloor%300 > 200 :
                #     time.sleep(20)
                #     self.send_comment(av_num, "盖楼")
                #     time.sleep(10)
                #     continue
                # if 300-topfloor%300 > 100 :
                #     time.sleep(20)
                #     self.send_comment(av_num, "盖楼")
                #     time.sleep(10)
                #     continue
                time.sleep(50)
        # 最新动态抢楼
        if award is False and av_num is None:
            exist = ''
            while 1:
                av_num, desc_type, upName, avType, avTitle, avDesc = self.get_newest()
                if av_num == "unkown":
                    print(av_num)
                    time.sleep(30)
                else:
                    print(av_num)
                    (comment_num, reply_type) = self.get_comment_num(av_num, desc_type)
                    print(comment_num)
                    if comment_num < 1 and exist != av_num:
                        # 随机评论，避免被吞
                        content = random.choice(['先赞后看(｀・ω・´)~', '已阅(o゜▽゜)o☆', '好看爱看(๑•̀ㅂ•́)و✧', '前来支持ฅʕ•̫͡•ʔฅ', '每集必看 ( ´͈ ᵕ ͈ )◞♡', '今日打卡ฅ՞• •՞ฅ', '不错不错₍ᐢ •̥ ̫ •̥ ᐢ₎', '不愧是你( ⁼̴̀ .̫ ⁼̴ )✧', '每日必看 ( ´͈ ᵕ ͈ )◞♡', '好看好看 ( ´͈ ᵕ ͈ )◞♡'])
                        self.send_comment(av_num, content, reply_type, upName, avType, avTitle, avDesc)
                        exist = av_num
                time.sleep(30)
        # 指定动态 + 指定楼层
        else:
            floor = 55
            if floor != 0:
                while 1:
                    comment_num, reply_type = self.get_comment_num(av_num, reply_type)
                    print("now is " + time.asctime(time.localtime(time.time())))
                    print("comment-num:" + str(comment_num))
                    if comment_num + 1 == floor:
                        self.send_comment(av_num, content, reply_type)
                        break
                    if comment_num >= floor:
                        print('被别人抢了。。')
                        break
                    time.sleep(1)


# cookies = read_cookie('./bilicookies')[0]
cookies = ""
# 发送评论需使用csrf，可从cookie获取
csrf = ""
# 推送平台配置
pushPlusToken = ""
serverPushToken = "" 

def task(cookies, csrf, pushPlusToken, serverPushToken):
    bi = BILI(cookies, csrf, pushPlusToken, serverPushToken)
    bi.run(content="(｀・ω・´)~")
    #upName, avType, avTitle, avDesc = bi.get_dynamic(1101219192, 1)
    # bi.run(av_num='24075101',floor=313,content="biu~")
    # bi.run(av_num='4265329',content="祝福~", award=True)
    # bi.run('8562550', floor=266)
    #av_num, reply_type =  bi.get_newest()
    # reply_count = bi.get_comment_num(av_num, reply_type)
    #bi.run(av_num, floor=101, content="biu~", award=False, reply_type=reply_type)
    # bi.send_comment(bi.get_newest(),"什么")
    # bi.run(floor=1)
    # bi.run()
    # bi.run('8562550',floor=270)


pool = ThreadPool(1)
for i in xrange(1):
    result = pool.apply_async(task, (cookies, csrf, pushPlusToken, serverPushToken))
    time.sleep(1)
pool.close()
pool.join()
