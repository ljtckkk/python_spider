# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import pymongo

# Item Pipeline 为项目管道。当 Item 生成后，它会自动被送到 Item Pipeline 进行处理
# 要实现 Item Pipeline ，只需要定义一个类并实现 process_item() 方法即可。
# 启用 Item Pipeline 后，Item Pipeline 会自动调用这个方法。process_item() 方法必须返回包含数据的字典或 Item 对象，或者抛出 DropItem 异常。
class TextPipeline(object):
    def __init__(self):
        # 定义最大返回的名言字符串长度
        self.limit = 50

    # process_item() 方法有两个参数。一个参数是 item，每次 Spider 生成的 Item 都会作为参数传递过来。另一个参数是 spider，就是 Spider 的实例。
    def process_item(self, item, spider):
        # 判断item是否存在
        if item['text']:
            # 判断item长度
            if len(item['text']) > self.limit:
                # .rstrip() 方法删除字符串末尾的指定字符，默认为空格
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')

# 存储数据的Item Pipeline
class MongoPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    # from_crawler，这是一个类方法，用 @ classmethod标识，是一种依赖注入的方式，方法的参数就是crawler，
    # 通过crawler这个我们可以拿到全局配置的每个配置信息，在全局配置settings.py中我们可以定义MONGO_URI和MONGO_DB来指定MongoDB
    # 连接需要的地址和数据库名称，拿到配置信息之后返回类对象即可。所以这个方法的定义主要是用来获取settings.py中的配置的。
    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_url=crawler.settings.get('MONGO_URL'),
                   mongo_db=crawler.settings.get('MONGO_DB')
                   )

    # open_spider，当Spider被开启时，这个方法被调用。在这里主要进行了一些初始化操作。
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.admin_db = self.client.admin                                       # 先连接系统默认数据库
        self.admin_db.authenticate("admin", "admin123",mechanism='SCRAM-SHA-1') # 让admin数据库去认证密码登录
        self.db = self.client[self.mongo_db]                                    # 再连接创建的数据库


    # 首先用self.__class__将实例变量指向类，然后再去调用__name__类属性（即获取类的名字）
    def process_item(self, item, spider):
        name = item.__class__.__name__      # 这里主要用类的名字当表名
        self.db[name].insert(dict(item))
        return item

    # close_spider，当Spider被关闭时，这个方法会调用，在这里将数据库连接关闭。
    def close_spider(self, spider):
        self.client.close()