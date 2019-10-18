# -*- coding: utf-8 -*-
# 存储数据的Item Pipeline
import pymongo


class MongoPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_url=crawler.settings.get('MONGO_URL'),
                   mongo_db=crawler.settings.get('MONGO_DB')
                   )

    # 连接数据库，item pipeline会自动调用这个方法
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.admin_db = self.client.admin                                       # 先连接系统默认数据库
        self.admin_db.authenticate("admin", "admin123",mechanism='SCRAM-SHA-1') # 让admin数据库去认证密码登录
        self.db = self.client[self.mongo_db]                                    # 再连接创建的数据库



    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))     # 向表中插入数据，如果这个表不存在会自动创建，如果已存在，则向表中插入数据
        print('Saved Mongo Success')
        return item

    # close_spider，当Spider被关闭时，这个方法会调用，在这里将数据库连接关闭。
    def close_spider(self, spider):
        self.client.close()