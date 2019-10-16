import re
import time

from taobao.login import login_taobao, browser, wait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from pyquery import PyQuery as pq
from pymongo import MongoClient

KEYWORD = '被子'
INDEX_START = 1

MONGO_DB = '淘宝'
MONGO_COLLECTION = KEYWORD

client = MongoClient('mongodb://admin:admin123@192.168.10.11:27017/')
db = client[MONGO_DB]

base_url = login_taobao()
# 拼接完整URL,quote将内容转换为URL编码格式，防止中文乱码
url = base_url + quote(KEYWORD)
browser.get(url)


def index_page(page):
    """
    抓取索引页
    :param page: 页码
    """
    print(' 正在爬取第 ', page, ' 页 ')
    try:
        # url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)

        if page > 1:
            # 获取页码输入框
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form> input')))
            # 获取'确定'按钮
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form> span.btn.J_Submit')))
            # 清空页码输入框
            input.clear()
            # 输入页码
            input.send_keys(page)
            # 点击确定
            submit.click()

        # 判断元素中是否包含指定文本，这里表示判断是否跳转到指定分页。EC模块中text_to_be_present_in_element专门用来判断
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        # 加载每个产品信息块
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    """提取商品数据"""
    html = browser.page_source
    doc = pq(html)
    # 用'#mainsrp-itemlist .items .item'这个生成器，以列表的形式返回可遍历的key,value元组，例：{('age': '20'), (''age': '22')}
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        # print(item)
        product = {'image': item.find('.pic .img').attr('data-src'),
                   'price': item.find('.price').text(),
                   'deal': item.find('.deal-cnt').text(),
                   'title': item.find('.title').text(),
                   'shop': item.find('.shop').text(),
                   'location': item.find('.location').text()}
        # print(product)
        save_to_mongo(product)


def save_to_mongo(product):
    try:
        # 创建表并插入数据
        if db[MONGO_COLLECTION].insert_one(product):
        # collection.insert_one(product)
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')


def get_max_index():
    total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
    print(total.text)
    index_text = re.search('(\d+)', total.text)
    max_index = index_text.group(1)
    print(max_index)
    for i in range(INDEX_START, int(max_index) + 1):
        time.sleep(30)
        index_page(i)


def main():
    get_max_index()


if __name__ == '__main__':
    main()
