# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# 存储数据的Item Pipeline
import pymongo

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class MongoPipeline(object):
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    '''
    from_crawler，这是一个类方法，用 @ classmethod标识，是一种依赖注入的方式，方法的参数就是crawler，
    通过crawler这个我们可以拿到全局配置的每个配置信息，在全局配置settings.py中我们可以定义MONGO_URI和MONGO_DB来指定MongoDB连
    接需要的地址和数据库名称，拿到配置信息之后返回类对象即可。所以这个方法的定义主要是用来获取settings.py中的配置的。
    '''
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


    # 首先用self.__class__将实例变量指向类，然后再去调用__name__类属性（即获取类的名字）
    def process_item(self, item, spider):
        self.db[item.collection].insert(dict(item))     # 向表中插入数据，如果这个表不存在会自动创建，如果已存在，则向表中插入数据
        print('Saved Mongo Success')
        return item

    # close_spider，当Spider被关闭时，这个方法会调用，在这里将数据库连接关闭。
    def close_spider(self, spider):
        self.client.close()


# 重写内置的ImagePipeline，方法都是重写父类方法
class ImagePipeline(ImagesPipeline):

    # 第一个参数 request 就是当前下载对应的 Request 对象。用splist()方法获取文件名
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    # 当单个 Item 完成下载时的处理方法。需要分析下载结果并剔除下载失败的图片。如果某张图片下载失败，那么我们就不需保存此 Item 到数据库。
    # 该方法的第一个参数 results 就是该 Item 对应的下载结果，它是一个列表形式，列表每一个元素是一个元组，其中包含了下载成功或失败的信息。
    # 遍历下载结果找出所有成功的下载列表。如果列表为空，那么该 Item 对应的图片下载失败，随即抛出异常 DropItem，该 Item 忽略。否则返回该 Item，说明此 Item 有效。
    def item_completed(self, results, item, info):
        print(results)
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item

    # 它的第一个参数item是爬取生成的Item对象。我们将它的url字段取出来，然后直接生成Request对象。此Request加入到调度队列，等待被调度，执行下载。
    def get_media_requests(self, item, info):
        yield Request(item['url'])