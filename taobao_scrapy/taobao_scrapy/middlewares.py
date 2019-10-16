# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger


class SeleniumMiddleware(object):

    # 2. 初始化属性、淘宝登录
    def __init__(self, timeout=None, weibo_username=None, weibo_password=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.weibo_username = weibo_username
        self.weibo_password = weibo_password

        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--start-maximized')
        self.browser = webdriver.Chrome(options=self.chrome_options)
        # self.browser.set_window_size(1400, 700)
        self.wait = WebDriverWait(self.browser, self.timeout)

        self.browser.get('https://login.taobao.com/member/login.jhtml')
        self.logger.debug('Chrome is Starting')

        # 获取'密码登录'按钮并点击
        # password_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
        # password_login.click()

        # 获取'微博登录'按钮并点击
        weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_OtherLogin > a.weibo-login')))
        weibo_login.click()

        # 获取'账号输入框'并输入账号
        EMAIL = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(2) > div > input')))
        EMAIL.send_keys(self.weibo_username)

        # 获取'密码输入框'并输入账号
        PASSWD = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(3) > div > input')))
        PASSWD.send_keys(self.weibo_password)

        # 获取'登录'按钮并点击
        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a > span')))
        button.click()
        time.sleep(5)

        # 获取用户名并打印
        # taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
        #                                                               '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # print(taobao_name.text)

    # 1. 取settings中的变量，返回给这个类
    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   weibo_username=crawler.settings.get('WEIBO_USERNAME'),
                   weibo_password=crawler.settings.get('WEIBO_PASSWORD'))


    def process_request(self, request, spider):

        """
            用 Chrome 抓取页面
            :param request: Request 对象
            :param spider: Spider 对象
            :return: HtmlResponse
        """

        page = request.meta.get('page', 1)

        try:
            self.browser.get(request.url)

            if page > 1:
                # 获取页码输入框
                input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form> input')))
                # 获取'确定'按钮
                submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form> span.btn.J_Submit')))
                # 清空页码输入框
                input.clear()
                # 输入页码
                input.send_keys(page)
                # 点击确定
                submit.click()

            # 判断元素中是否包含指定文本，这里表示判断是否跳转到指定分页。EC模块中text_to_be_present_in_element专门用来判断
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
            # 加载每个产品信息块
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))

            # HtmlResponse是Response的子类，相当于返回了一个Response对象。此时其他的DownLoader Middlewares的process_request便不会再继续调用了
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8', status=200)

        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    def __del__(self):
        self.browser.close()



