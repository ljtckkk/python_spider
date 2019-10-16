import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient

KEYWORD = '推送动态'
MONGO_DB = '码云'
MONGO_COLLECTION = KEYWORD
client = MongoClient('mongodb://admin:admin123@192.168.10.11:27017/')
db = client[MONGO_DB]


class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'http://gitee.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Host': 'gitee.com'
        }
        self.login_url = 'https://gitee.com/login'
        self.post_url = 'https://gitee.com/login'
        self.setting_url = 'https://gitee.com/profile'
        self.feed_url = 'https://gitee.com/ljpython/event_list?url=%2Fljpython%2Fevent_list&scope=all&day=&start_date=&end_date=&year=&per_page=20&page=1'
        # requests库的session对象能够帮我们跨请求保持某些参数，也会在同一个session实例发出的所有请求之间保持cookies。
        self.session = requests.Session()

    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        # 构造一个XPath解析对象并对HTML文本进行自动修正
        selector = pq(response.text)
        # 输出修正后的结果，类型是bytes
        # 取出authenticity_token的value
        token = selector('input[name=authenticity_token]').attr('value')
        return token

    def login(self, email, password):
        token = self.token()
        # 构造表单
        post_data = {
            # 'commit': 'Sign in',      # 这个field用于GitHub，目前还未解决422状态码问题
            'utf8': '✓',
            'authenticity_token': token,
            'user[login]': email,
            'user[password]': password
        }

        # 使用post方法将表单发布给服务器
        login_response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        # 找到Ajax请求的URL，得到关注人的动态信息
        response = self.session.get(self.feed_url, headers=self.headers)
        # 判断登录状态码
        if login_response.status_code == 200:
            print('登录成功')
            # 判断 Ajax请求的URL状态码
            if response.status_code == 200:
                # 调用dynamics里的生成器
                for result in self.dynamics(response.json()):
                    # 保存到数据库
                    self.save_to_mongo(result)

        # 获取设置页面页面
        response = self.session.get(self.setting_url, headers=self.headers)
        # 判断状态码
        if response.status_code == 200:
            result = self.profile(response.text)
            print(result)

    # 关注人的动态信息
    def dynamics(self, html):
        dynamics = html
        # 提取非评论动态，如果需要提取评论动态，可以再建一个comment方法
        for item in dynamics:
            try:
                yield {'name': item.get('author').get('name'),
                       'created_at': item.get('created_at'),
                       'project': item.get('project').get('name_with_namespace'),
                       'status': item.get('status').get('name'),
                       'path': 'https://gitee.com' + item.get('target').get('path'),
                       'title': item.get('target').get('title'),
                       }
            except Exception:
                pass

    # 设置页面信息
    def profile(self, html):
        selector = pq(html)
        # 提取当前登录账号的姓名
        name = '用户名：' + selector('div[class="field"] input[id="user_name"]').attr('value')
        # 提取当前账号的绑定手机号
        phone = '手机号' + selector('div[class="field inline"] input[id="phone-input"]').attr('value')
        return name, phone

    # 保存至数据库
    def save_to_mongo(self, item):
        # 创建表并插入数据
        if db[MONGO_COLLECTION].insert_one(item):
            # collection.insert_one(product)
            print('存储到MongoDB成功')


if __name__ == "__main__":
    login = Login()
    login.login(email='jsjsboy@sina.com', password='yuting123')
