# -*- coding: utf-8 -*-
import scrapy


class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['www.google.com']
    start_urls = ['http://www.google.com/']

    # 重写start_requests方法，定义request超时时间、回调函数、过滤参数
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'download_timeout': 10}, callback=self.parse, dont_filter=True)

    def parse(self, response):
        print(response.text)
        print(response.status)
