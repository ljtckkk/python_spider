# -*- coding: utf-8 -*-
import scrapy

from tutorial.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    # 项目名
    name = 'quotes'
    # 允许爬取的域名
    allowed_domains = ['quotes.toscrape.com']
    # spider在启动时爬取的url列表
    start_urls = ['http://quotes.toscrape.com/']

    # 被调用时start_urls里面的链接构成的请求完成下载执行后，返回的响应就会作为唯一的参数传递给这个函数。该方法负责解析返回的响应、提取数据或者进一步生成要处理的请求。
    def parse(self, response):
        # print(response.text)
        quotes = response.css('.quote')
        for quote in quotes:
            item = QuoteItem()
            text = quote.css('.text::text').extract_first()
            author = quote.css('.author::text').extract_first()
            # 由于tag有多个值，所以使用extract()取当前的所有值
            tags =  quote.css('.tags .tag::text').extract()

            item['text'] = text
            item['author'] = author
            item['tags'] = tags
            yield item

        # 获取下一页的url;
        next = response.css('.pager .next a::attr(href)').extract_first()
        # 将一个相对url构造成一个绝对url，例如这里获取的是next是/page/2， 通过urljoin会变成http://quotes.toscrape.com/page/2
        url = response.urljoin(next)
        # 重新构造请求使用scrapy.Request()，这里是2个参数，一个url，一个回调函数
        yield scrapy.Request(url=url, callback=self.parse)

