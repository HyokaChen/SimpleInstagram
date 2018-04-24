#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 @File       : spider.py
 @Time       : 2017/8/12 0012 21:22
 @Author     : Empty Chan
 @Contact    : chen19941018@gmail.com
 @Description:
"""
import re
import json
import os
from lxml import etree
import requests
import click
from urllib import parse
import time
from hashlib import md5
import random

from utils import ctx

PAT = re.compile(r'queryId:"(.+?)",', re.MULTILINE)
headers = {
    "Origin": "https://www.instagram.com/",
    "Referer": "https://www.instagram.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
    "Host": "www.instagram.com",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, sdch, br",
    "accept-language": "zh-CN,zh;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Upgrade-Insecure-Requests": "1",
}

jso = {"id": "", "first": 12, "after": ""}

BASE_URL = "https://www.instagram.com"

# QUERY = "/morisakitomomi/"  # 森咲智美
# QUERY = "/_8_jjini/"
NEXT_URL = 'https://www.instagram.com/graphql/query/?query_hash={0}&variables={1}'

with open('./config.json', 'r') as f:
    proxy = json.load(f)
    click.echo(proxy)

# 没有爬取全部则不进行文件的读写
IS_ALL_COMPLETE = False


def crawl(query):
    if not query:
        raise Exception('请输入正确的Instagram用户')
    folder = query.replace('.', '-')
    click.echo('start...')
    top_url = None
    in_top_url_flag = False
    qq = requests.session()
    try:
        if not os.path.exists('./images/%s' % folder):
            os.mkdir('./images/%s' % folder)
        new_imgs_url = []
        all_imgs_url = []
        if os.path.exists('./images/%s/%s.txt' % (folder, folder)):
            with open('./images/%s/%s.txt' % (folder, folder), mode='r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.strip():
                        all_imgs_url.append(line)
            if IS_ALL_COMPLETE:
                top_url = all_imgs_url[0][:-1]
        temp_url = BASE_URL + '/' + query + '/'
        headers.update({'Referer': temp_url})
        res = qq.get(temp_url, headers=headers, proxies=proxy)
        html = etree.HTML(res.content.decode())
        all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')  # 图片数据源
        query_id_url = html.xpath('//script[@type="text/javascript"]/@src')  # query_id 作为内容加载
        click.echo(query_id_url)
        for a_tag in all_a_tags:
            if a_tag.strip().startswith('window'):
                data = a_tag.split('= {')[1][:-1]  # 获取json数据块
                js_data = json.loads('{' + data, encoding='utf-8')
                id = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
                edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
                print(edges)
                end_cursor = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                has_next = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                for edge in edges:
                    if top_url and top_url == edge["node"]["display_url"]:
                        in_top_url_flag = True
                        break
                    click.echo(edge["node"]["display_url"])
                    new_imgs_url.append(edge["node"]["display_url"])
                    # click.echo(qq.get(node["display_src"], proxies=proxy).status_code)
                rhx_gis = js_data["rhx_gis"]
                if in_top_url_flag:
                    break
                # 请求query_id
                print(BASE_URL + query_id_url[1])
                query_content = qq.get(BASE_URL + query_id_url[1], proxies=proxy)
                query_id_list = PAT.findall(query_content.text)
                for u in query_id_list:
                    click.echo(u)
                # 看起来使用的是第二个hash
                query_hash = query_id_list[1]
                print(query_hash)
                # 暂时不确定3个query_hash具体用哪个,目前看网页的情况是固定的
                # query_hash = "472f257a40c653c64c666ce877d59d2b"
                retry = 0
                # 加载更多
                new_imgs_url = load_more(qq, id, has_next, query_hash, rhx_gis, end_cursor, top_url, in_top_url_flag, retry)
        if len(new_imgs_url):
            print('enter.....')
            all_urls = new_imgs_url + all_imgs_url
            with open('./images/%s/%s.txt' % (folder, folder), mode='w+', encoding='utf-8') as f:
                for u in all_urls:
                    f.write(u + '\n')
        translate(top_url, new_imgs_url, all_imgs_url, query)
    except Exception as e:
        raise e
    finally:
        qq.close()


def load_more(session, id, has_next, query_hash, rhx_gis, end_cursor, top_url, in_top_url_flag, retry):
    new_imgs_url = []
    # 更多的图片加载
    while has_next and not in_top_url_flag:
        jso["id"] = id
        jso["first"] = 12
        jso["after"] = end_cursor
        # 注意了这处dumps默认会出都自动在，逗号和冒号后面添加空格，导致了格式不符合
        text = json.dumps(jso, separators=(',', ':'))
        xhr_code = "{0}:{1}".format(rhx_gis, text)
        print(xhr_code)
        # for query_hash in query_id_list:
        url = NEXT_URL.format(query_hash, parse.quote(text))
        print(url)
        gis = ctx.call("get_gis", xhr_code)
        # 就是缺少了这个GIS参数
        headers.setdefault("X-Instagram-GIS", gis)
        headers.update({"X-Instagram-GIS": gis})
        res = None
        while retry < 3:
            try:
                res = session.get(url, headers=headers, proxies=proxy)
            except Exception as e:
                print('error >>%s' % url)
                time.sleep(random.random() * 2)
        time.sleep(random.random() * 2)
        if res is None:
            return new_imgs_url
        print(res.status_code)
        html = json.loads(res.content.decode(), encoding='utf-8')
        if '<' in html:  # 出现HTML tag
            continue
        if 'data' not in html:  # data不再json数据中，可能是网络请求引发，进行重试请求
            retry += 1
            continue
        has_next = html["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
        end_cursor = html["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        edges = html["data"]["user"]["edge_owner_to_timeline_media"]["edges"]

        for edge in edges:
            if top_url and top_url == edge["node"]["display_url"]:
                in_top_url_flag = True
                break
            click.echo(edge["node"]["display_url"])
            new_imgs_url.append(edge["node"]["display_url"])
    click.echo('ok')
    return new_imgs_url


def translate(top_url, news_imgs_url, all_imgs_url, path):
    if news_imgs_url:
        click.echo('enter news')
        download(path, news_imgs_url)
    if top_url:
        # file_md5 = md5()
        # file_md5.update(top_url.encode('utf-8'))
        # file_name = file_md5.hexdigest()
        # if os.path.exists('./images/%s/%s.jpg' % (path, file_name)):
        #     return
        # else:
        click.echo('enter all')
        download(path, all_imgs_url)


def download(path, urls):
    ss = requests.session()
    temp_url = BASE_URL + '/' + path + '/'
    folder = path.replace('.', '-')
    header = {
        "Referer": temp_url,
        "Origin": "https://www.instagram.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/60.0.3112.113 Safari/537.36",
        'Connection': 'keep-alive'
    }
    pp = ss.get(temp_url, headers=header, proxies=proxy)
    click.echo(pp.cookies.items())
    click.echo(pp.headers)
    try:
        count = 0
        all_count = len(urls)
        while count < all_count:
            url = urls[count]
            if '\n' in url:
                url = urls[count][:-1]  # 去掉\n结尾
            file_md5 = md5()
            file_md5.update(url.encode('utf-8'))
            file_name = file_md5.hexdigest()
            if os.path.exists('./images/%s/%s.jpg' % (folder, file_name)):
                count += 1
                continue
            time.sleep(random.random() * 2)
            res = ss.get(url, headers=headers, proxies=proxy)  # 默认沿用请求首页的cookies
            click.echo(url + '=>' + str(res.status_code))
            click.echo(res.headers)
            if res.status_code == 200:
                with open('./images/%s/%s.jpg' % (folder, file_name), mode='wb') as f:
                    f.write(res.content)
                    click.echo('%s.jpg save!' % file_name)
                    count += 1
            else:
                ss.close()
                ss = requests.session()
                pp = ss.get(temp_url, headers=header, proxies=proxy)
                click.echo(pp.cookies.items())
                click.echo(pp.headers)
            if count % 100 == random.randrange(20, 50):  # 请求超过20-50次，就重置一下session，防止被远程服务器关闭
                ss.close()
                ss = requests.session()
                pp = ss.get(temp_url, headers=header, proxies=proxy)
                click.echo(pp.cookies.items())
                click.echo(pp.headers)
        click.echo('complete!')
    except Exception as e:
        raise e
    finally:
        ss.close()


# {'Content-Type': 'text/html; charset=utf-8', 'Access-Control-Allow-Origin': '*', 'Date': 'Tue, 29 Aug 2017 14:44:00 GMT', 'X-FB-Edge-Debug': '0SgdqUrVrprsJ061ZnHRWlTHLqBwZfkyOVnIOpk3HiaW9AWZ8Gpk1TAiRJP1kHAQCsB59J08egc44qA8JEZS0Q', 'Connection': 'keep-alive', 'Content-Length': '105'}

# def download(path, urls):
#     temp_url = BASE_URL + '/' + path + '/'
#     cookie = cookiejar.CookieJar()  # 声明一个CookieJar对象实例来保存cookie
#     handler = urllib.request.HTTPCookieProcessor(cookie)  # 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
#     header = {
#         "Referer": temp_url,
#         "Origin": "https://www.instagram.com/",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                       "Chrome/60.0.3112.113 Safari/537.36",
#         'Connection': 'keep-alive'
#     }
#     proxy_handler = urllib.request.ProxyHandler(proxy)
#     opener = urllib.request.build_opener(proxy_handler)  # 挂载opener
#     opener.add_handler(handler)
#     urllib.request.install_opener(opener)  # 安装opener
#     # headers.update({'Referer': BASE_URL + '/' + path + '/'})
#
#     pp = opener.open(temp_url)
#     click.echo(pp.info())
#     try:
#         count = 0
#         all_count = len(urls)
#         while count < all_count:
#             url = urls[count][:-1]  # 去掉\n结尾
#             file_md5 = md5()
#             file_md5.update(url.encode('utf-8'))
#             file_name = file_md5.hexdigest()
#             if os.path.exists('E:\\kankan\\%s\\%s.jpg' % (path, file_name)):
#                 count += 1
#                 continue
#             time.sleep(2)
#             res = opener.open(url)  # 默认沿用请求首页的cookies
#             click.echo(url + '=>' + str(res.code))
#             click.echo(res.code)
#             # if res.status_code == 400:
#             #     click.echo(res.text)
#             if res.code == 200:
#                 with open('E:\\kankan\\%s\\%s.jpg' % (path, file_name), mode='wb') as f:
#                     f.write(res.read())
#                     click.echo('%s.jpg save!' % file_name)
#                     count += 1
#         click.echo('complete!')
#     except Exception as e:
#         raise e


if __name__ == '__main__':
    # 'morisakitomomi'
    input_instagram = click.prompt("请输入Instagram用户", None)
    crawl(input_instagram)

