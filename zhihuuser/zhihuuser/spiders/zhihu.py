# -*- coding: utf-8 -*-
import json
import logging
import time
import requests
import scrapy

from scrapy import Request
from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']

    start_urls = ['http://www.zhihu.com/']
    start_user = 'lucky-60-21'

    # 用户详细信息url
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    # 关注列表用户url
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    # 粉丝列表url
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        logger = logging.getLogger(__name__)
        logger.debug("Let's go")
        # １. 先获取一个用户的详细信息
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse)
        # 2. 再获取这个用户的关注列表
        yield Request(url=self.follows_url.format(user=self.start_user, include=self.follows_query, limit=20, offset=0), callback=self.follows_user)
        # 获取用户粉丝列表
        yield Request(url=self.followers_url.format(user=self.start_user, include=self.followers_query, limit=20, offset=0), callback=self.followers_user)

    def parse(self, response):
        # time.sleep(0.5)
        result = json.loads(response.text)
        item = UserItem()
        # 1.1 从item.fields循坏取出Item的field。
        # 1.2 判断field是否在result.keys()中。
        # 1.3 对item赋值，使
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        # 4. 对这个用户的关注人列表再发起请求，回调函数是follows_user，这样再可获取这个用户的所有关注人的详细信息
        yield Request(url=self.follows_url.format(user=('url_token'), include=self.follows_query, limit=20, offset=0), callback=self.follows_user)
        # 对这个用户的粉丝列表再发起请求
        yield Request(url=self.followers_url.format(user=('url_token'), include=self.followers_query, limit=20, offset=0), callback=self.followers_user)

    # 处理关注用户方法
    def follows_user(self, response):
        '''
        3. 循环取出每个关注页的每个用户详细信息
        5．找到所有的分页URL并发起请求
        :param response:
        :return:
        '''
        results = json.loads(response.text)
        # 判断data字段是否存在
        if 'data' in results.keys():
            # 循环取出data字段里面所有用户信息
            for result in results.get('data'):
                # 重新发起request获取每个用户的详细信息
                yield Request(url=self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse)

        # 判断'paging'自断是否存在，并且'paging'的'is_end'字段值是不是False。该字段为True时表示是最后一页
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            #在'paging'中的'next'字段写明了下一页的地址，不过知乎对这个URL做了改写，将其中的'/api/v4/'去掉了，下面对其重构
            url_str = results.get('paging').get('next')
            url_split = url_str.split('com/')
            next_page =url_split[0] + 'com/api/v4/' + url_split[1]

            yield Request(url=next_page, callback=self.follows_user)

    # 处理粉丝方法
    def followers_user(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(url=self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(url=next_page, callback=self.followers_user)
