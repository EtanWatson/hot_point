import json
import re
from json import JSONDecodeError
from urllib.parse import urlencode

import requests
import time
from bs4 import BeautifulSoup
from requests import RequestException
# 开启多线程
from multiprocessing import Pool
import pymongo

from util import getASCP, get_as_cp
from config import *
import config

# 数据库相关
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

s = requests.session()


def get_page_index(max_behot_time, max_behot_time_tmp, as_1, cp):
    """解析索引页面"""
    data = {
        'category': 'news_hot',
        'utm_source': 'toutiao',
        'widen': 1,
        'max_behot_time': max_behot_time,
        'max_behot_time_tmp': max_behot_time_tmp,
        'tadrequire': 'true',
        'as': as_1,
        'cp': cp
    }
    url = 'https://www.toutiao.com/api/pc/feed/?' + urlencode(data)
    # print(url)
    try:

        response = s.get(url)

        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页面出错！')
        return None


def parse_page_index(html):
    """解析索引页面"""
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                # yield生成器
                yield item.get('source_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    """获取详情页"""
    try:
        response = s.get(WEB_URL + url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页面出错！', url)
        return None


def parse_article_info(article_info_pattern, title):
    """解析content数据"""
    if len(article_info_pattern) > 0:
        article_info = article_info_pattern[0]
        content_parse = re.compile('content: (.*?)groupId', re.S)
        is_origin_parse = re.compile('isOriginal: (.*?),', re.S)
        source_parse = re.compile('source: (.*?),', re.S)
        time_parse = re.compile('time: (.*?)}', re.S)
        article_info_map = {
            'title': title,
            'content': re.findall(content_parse, article_info)[0],
            'is_origin': re.findall(is_origin_parse, article_info)[0],
            'source': re.findall(source_parse, article_info)[0],
            'time': re.findall(time_parse, article_info)[0]
        }
        # print(article_info_map)
        save_to_mongo(article_info_map)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存MONGONDB成功', result)
    except Exception:
        print('保存到MONGODB失败', result)


def parse_page_detail(html, url):
    """解析详情页"""
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    # print(title)
    article_info_pattern = re.compile('articleInfo: {.*?},', re.S)
    article_info = re.findall(article_info_pattern, html)
    parse_article_info(article_info, title)


# def parse_next(html):
#     next_parse = re.compile('"max_behot_time": (.*?)}')
#     NEXT = int(re.findall(next_parse, html)[0])
#     print(NEXT)


def main():
    # page_num = 0
    while True:
        try:
            AS, CP = getASCP()
            html = get_page_index(config.NEXT, config.NEXT, AS, CP)
            next_parse = re.compile('"max_behot_time": (.*?)}')
            config.NEXT = int(re.findall(next_parse, html)[0])
            for url in parse_page_index(html):
                if re.compile('(http:.*?)').search(url) or re.compile('(https:.*?)').search(url):
                    continue
                html = get_page_detail(url)
                if html:
                    parse_page_detail(html, url)
        except Exception:
            config.NEXT = 0
            main()


if __name__ == '__main__':
    main()
