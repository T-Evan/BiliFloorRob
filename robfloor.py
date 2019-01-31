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
    def __init__(self, Cookie, csrf):
        self.s = requests.Session()
        self.Cookie = Cookie
        self.csrf = csrf
        # 重试
        request_retry = HTTPAdapter(max_retries=3)
        self.s.mount('http://', request_retry)

    def get_comment_num(self, av_num, desc_type):
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': self.Cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Host': 'api.bilibili.com'
        }
        reply_type = 0
        try:
            if desc_type == 16:
                reply_type = 5
            elif desc_type == 2:
                reply_type = 11
            elif desc_type == 4 or desc_type == 1:
                reply_type = 17
            elif desc_type == 8:
                reply_type = 1
            r = self.s.get(
                'http://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=' + str(reply_type) + '&sort=0&oid=' + av_num,
                headers=header)
            replies = r.json()['code']
            if replies == 0:  # 继续判断是否为转发动态
                if r.json()['data']['replies']:
                    return (r.json()['data']['replies'][0]['floor'], reply_type)
                else:
                    return 0, reply_type
            else:
                return "get_comment_num unkown desc_type"
        except Exception as e:
            print(e)
            print(r)
            # exit()

    def send_comment(self, av_num, message, reply_type):
        header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
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
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?uid=326196181&type=268435455"
        try:
            # r = self.s.get(url, proxies={'http': random.choice(pro)},  headers=header)
            r = self.s.get(url, headers=header)
            desc_type = r.json()['data']['cards'][0]['desc']['type']
            if desc_type == 8 or desc_type == 2 or desc_type == 16 or desc_type == 64:
                return str(r.json()['data']['cards'][0]['desc']['rid']), desc_type
            elif desc_type == 1 or desc_type == 4: #1为转发动态，4为纯文字动态，暂时无法获取用于评论的动态id
                return str(r.json()['data']['cards'][0]['desc']['dynamic_id_str']), desc_type
                # return ("unkown"),desc_type
                av_num = r.json()['data']['cards'][0]['card']
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
    def run(self, av_num=None, floor=0, content=None, award=False):

        if content is None:
            # '1楼精准打击～没有人能在我的关注里打败我，大大的flag233'
            content = "多线程~" + str(floor) + '楼精准打击～'
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
        if award is False and av_num is None:
            while 1:
                av_num, desc_type = self.get_newest()
                if av_num == "unkown":
                    print(av_num)
                    time.sleep(10)
                else:
                    print(av_num)
                    (comment_num, reply_type) = self.get_comment_num(av_num, desc_type)
                    print(comment_num)
                    if comment_num < 2:
                        self.send_comment(av_num, content, reply_type)
                time.sleep(10)
        else:
            if floor != 0:
                while 1:
                    comment_num = self.get_comment_num(av_num)
                    print("now is " + time.asctime(time.localtime(time.time())))
                    print("comment-num:" + str(comment_num))
                    if comment_num + 1 == floor:
                        self.send_comment(av_num, content)
                        break
                    if comment_num >= floor:
                        print('被别人抢了。。')
                        break
                    time.sleep(1)


# cookies = read_cookie('./bilicookies')[0]
cookies = ""
csrf = ""



def task(cookies, csrf):
    bi = BILI(cookies, csrf)
    bi.run(content="(｀・ω・´)~")
    # bi.run(av_num='24075101',floor=313,content="biu~")
    # bi.run(av_num='4265329',content="祝福~", award=True)
    # bi.run('8562550', floor=266)
    # print bi.get_comment_num(bi.get_newest())
    # bi.send_comment(bi.get_newest(),"什么")
    # bi.run(floor=1)
    # bi.run()
    # bi.run('8562550',floor=270)


pool = ThreadPool(1)
for i in xrange(1):
    result = pool.apply_async(task, (cookies, csrf,))
    time.sleep(1)
pool.close()
pool.join()
