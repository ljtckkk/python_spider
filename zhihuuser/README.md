
## 安装

使用pip安装以下包:

`pip install scrapy-redis-bloomfilter`


## 使用

参考settings中的配置:

# 使用scrapy_redis的调度器

`SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"`

去重类，已修改为布隆去重

`DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"`

哈希函数的个数，默认为 7，可以自行修改

`BLOOMFILTER_HASH_NUMBER = 7`

BloomFilter 的 bit 参数，默认 31，占用 256MB 空间，去重量级 1 亿

`BLOOMFILTER_BIT = 31`

是否在关闭时候保留原来的调度器和去重记录，True=保留，False=清空

`SCHEDULER_PERSIST = True`
