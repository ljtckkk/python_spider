# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request, Spider
from urllib.parse import quote
from taobao_scrapy.items import ProductItem
from pyquery import PyQuery as pq


class TaobaoSpider(Spider):
    name = 'taobao'
    allowed_domains = ['www.taobao.com']
    base_url = 'https://s.taobao.com/search?q='

    def start_requests(self):

        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield Request(url=url, callback=self.parse, meta={'page': page}, dont_filter=True)

    def parse(self, response):

        """提取商品数据"""
        html = response.text
        doc = pq(html)
        # 用'#mainsrp-itemlist .items .item'这个生成器，以列表的形式返回可遍历的key,value元组，例：{('age': '20'), (''age': '22')}
        products = doc('#mainsrp-itemlist .items .item').items()

        for product in products:
            item = ProductItem()
            item['image'] = product.find('.pic .img').attr('data-src')
            item['price']= product.find('.price').text()
            item['deal']=product.find('.deal-cnt').text()
            item['title']= product.find('.title').text()
            item['shop']= product.find('.shop').text()
            item['location']= product.find('.location').text()
            print(item)
            yield item

        # products = response.xpath('//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class, "item")]')
        # for product in products:
        #     item = ProductItem()
        #     item['price'] = ''.join(product.xpath('.//div[contains(@class, "price")]//text()').extract()).strip()
        #     item['title'] = ''.join(product.xpath('.//div[contains(@class, "title")]//text()').extract()).strip()
        #     item['shop'] = ''.join(product.xpath('.//div[contains(@class, "shop")]//text()').extract()).strip()
        #     item['image'] = ''.join(product.xpath('.//div[@class="pic"]//img[contains(@class, "img")]/@data-src').extract()).strip()
        #     item['deal'] = product.xpath('.//div[contains(@class, "deal-cnt")]//text()').extract_first()
        #     item['location'] = product.xpath('.//div[contains(@class, "location")]//text()').extract_first()
        #     print(item)
        #     yield item




