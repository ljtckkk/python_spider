from urllib.parse import urlencode
from pyquery import PyQuery as pq
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import re

url = 'https://m.weibo.cn'
base_url = 'https://m.weibo.cn/api/container/getIndex?'

client = MongoClient('mongodb://admin:admin123@192.168.10.11:27017/')
db = client['weibo']
collection = db['weibo']

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

'https://m.weibo.cn/api/container/getIndex?containerid=2304132830678474_-_WEIBO_SECOND_PROFILE_WEIBO&luicode=10000011&lfid=2302832830678474&page_type=03&page=2'


def get_page(page):
    params = {
        'containerid': '2304132830678474_-_WEIBO_SECOND_PROFILE_WEIBO',
        'luicode': '10000011',
        'lfid': '2302832830678474',
        'page_type': '03',
        'page': page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_page(json):

    if json:
        items = json.get('data').get('cards')
        for item in items:
            try:
                item = item.get('mblog')
                weibo = {'id': item.get('id'),
                         'text': pq(item.get('text')).text(),
                         'attitudes': item.get('attitudes_count'),
                         'comments': item.get('comments_count'),
                         'reposts': item.get('reposts_count')}
                # text = weibo['text']
                # print(text)
                # match_url = r'<a.*?href=(.*?)>'       # 匹配URL
                # text_one = r'全文'           # 匹配'全文'
                # all_text = re.search(text_one, text)
                # print(all_text.group())
                # if all_text.group() == '全文':
                #     print('开始匹配')
                #     part_url = re.search(match_url, text)
                #     print(part_url)
                # new_url = url + part_url
                # print(new_url)
                # response = requests.get(new_url).text
                yield weibo
            except Exception:
                pass


def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo')


if __name__ == '__main__':
    for page in range(1, 11):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            save_to_mongo(result)
            print(result)