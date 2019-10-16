import os
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

import requests
from pymongo import MongoClient

base_url = 'https://www.toutiao.com/api/search/content/?'

client = MongoClient('mongodb://admin:admin123@192.168.10.11:27017/')
db = client['头条']
collection = db['头条']

headers = {
    'Host': 'www.toutiao.com',
    'Referer': 'https://www.toutiao.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def get_page(page, name):
    params = {
        'offset': page,
        'format': 'json',
        'keyword': name,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
    }
    url = base_url + urlencode(params)
    print(url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {'image': image.get('url'),
                       'title': title
                       }


def save_image(item):
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image')


def main(offset):
    name = '街拍'
    json = get_page(offset, name)
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START = 0
GROUP_END = 20

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
