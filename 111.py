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
import random
from hashlib import md5
import urllib.request
from http import cookiejar
import urllib.response


PAT = re.compile(r'queryId:"(\d*)?"', re.MULTILINE)
headers = {
    "Origin": "https://www.instagram.com/",
    "Referer": "https://www.instagram.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Host": "www.instagram.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, sdch, br",
    "accept-language": "zh-CN,zh;q=0.8",
    "X-Instragram-AJAX": "1",
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

        all_imgs_url = []
        new_imgs_url = []
        if os.path.exists('./images/%s/%s.txt' % (folder, folder)):
            with open('./images/%s/%s.txt' % (folder, folder), mode='r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.strip():
                        all_imgs_url.append(line)
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
                nodes = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
                end_cursor = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                has_next = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                for node in nodes:
                    if top_url:
                        in_top_url_flag = True
                        break
                    click.echo(node["display_url"])
                    new_imgs_url.append(node["display_url"])
                    # click.echo(qq.get(node["display_src"], proxies=proxy).status_code)

                if in_top_url_flag:
                    break
                # 请求query_id
                query_content = qq.get(BASE_URL + query_id_url[0], proxies=proxy)
                query_id_list = PAT.findall(query_content.text)
                for u in query_id_list:
                    click.echo(u)
                query_hash = query_id_list[0]
                retry = 0
                # 更多的图片加载
                while has_next and retry < 3 and not in_top_url_flag:
                    jso["id"] = id
                    jso["first"] = 12
                    jso["after"] = end_cursor
                    text = json.dumps(jso)
                    url = NEXT_URL.format(query_hash, parse.quote(text))
                    res = qq.get(url, proxies=proxy)
                    time.sleep(2)
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
                # qq.close()
        if new_imgs_url:
            all_urls = new_imgs_url + all_imgs_url
            with open('./images/%s/%s.txt' % (folder, folder), mode='w', encoding='utf-8') as f:
                    for u in all_urls:
                        f.write(u + '\n')
        # t = threading.Thread(target=translate, args=(top_url, new_imgs_url, all_imgs_url, query))
        # t.setDaemon(True)
        # t.start()
        # t.join()
        translate(top_url, new_imgs_url, all_imgs_url, query)
    except Exception as e:
        raise e
    finally:
        qq.close()


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
            time.sleep(2)
            res = ss.get(url, proxies=proxy)  # 默认沿用请求首页的cookies
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

if __name__ == '__main__':
    input_instagram = click.prompt("请输入Instagram用户", None)  # 如 "/_8_jjini/"  等用户
    crawl(input_instagram)