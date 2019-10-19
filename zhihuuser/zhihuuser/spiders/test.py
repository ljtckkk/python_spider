# from redis import StrictRedis
#
#
# class HashMap(object):
#     def __init__(self, m, seed):
#         self.m = m
#         self.seed = seed
#
#     def hash(self, value):
#         """
#         Hash Algorithm
#         :param value: Value
#         :return: Hash Value
#         """
#         ret = 0
#         for i in range(len(value)):
#             ret += self.seed * ret + ord(value[i])
#         return (self.m - 1) & ret
#
#
# # BLOOMFILTER_HASH_NUMBER = 6
# # BLOOMFILTER_BIT = 30
#
# class BloomFilter(object):
#     def __init__(self, server, key, bit, hash_number):
#         """
#         Initialize BloomFilter
#         :param server: Redis Server
#         :param key: BloomFilter Key
#         :param bit: m = 2 ^ bit
#         :param hash_number: the number of hash function
#         """
#         # default to 1 << 30 = 10,7374,1824 = 2^30 = 128MB, max filter 2^30/hash_number = 1,7895,6970 fingerprints
#         self.m = 1 << bit
#         self.seeds = range(hash_number)
#         self.maps = [HashMap(self.m, seed) for seed in self.seeds]
#         self.server = server
#         self.key = key
#
#     def exists(self, value):
#         """
#         if value exists
#         :param value:
#         :return:
#         """
#         if not value:
#             return False
#         exist = 1
#         for map in self.maps:
#             offset = map.hash(value)
#             exist = exist & self.server.getbit(self.key, offset)
#         return exist
#
#     def insert(self, value):
#         """
#         add value to bloom
#         :param value:
#         :return:
#         """
#         for f in self.maps:
#             offset = f.hash(value)
#             self.server.setbit(self.key, offset, 1)
#
#
# if __name__ == '__main__':
#     conn = StrictRedis(host='localhost', port=6379, password='YUting@123')
#     bf = BloomFilter(conn, 'testbf', 5, 6)
#     bf.insert('Hello')
#     bf.insert('World')
#     result = bf.exists('Hello')
#     print(bool(result))
#     result = bf.exists('Python')
#     print(bool(result))


from scrapy import Request, Spider

class TestSpider(Spider):
    name = 'test'
    base_url = 'https://www.baidu.com/s?wd='

    def start_requests(self):
        for i in range(10):
            url = self.base_url + str(i)
            yield Request(url, callback=self.parse)

        # Here contains 10 duplicated Requests
        for i in range(100):
            url = self.base_url + str(i)
            yield Request(url, callback=self.parse)

    def parse(self, response):
        self.logger.debug('Response of ' + response.url)