import time
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying
from config import *


class Crack12306():

    def __init__(self):
        self.url = 'https://kyfw.12306.cn/otn/login/init'
        self.browser = webdriver.Chrome()
        # self.browser.set_window_size(1920, 1080)
        self.wait = WebDriverWait(self.browser, 20)
        self.username = USERNAME
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def __del__(self):
        print('正在关闭浏览器')
        time.sleep(10)
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        username.send_keys(self.username)
        password.send_keys(self.password)

    def get_12306_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.touclick .touclick-image')))
        return element

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_12306_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_12306_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 裁剪后的图片对象
        """
        top, bottom, left, right = self.get_position()
        print(' 验证码位置 ', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_points(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        # get_points()将识别结果变成列表的形式。
        # 超级鹰识别后返回结果：{'err_no': 0, 'err_str': 'OK', 'pic_id': '9082718423155200001', 'pic_str': '55,152|176,148', 'md5': '508d3222a99aa1a5218ccbfcda3a2857'}
        groups = captcha_result.get('pic_str').split('|')
        print(groups)
        # locations = [[55, 152],[176, 148]]
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        # touch_click_words()方法则通过调用move_to_element_with_offset()方法依次传入解析后的坐标，点击即可。
        element = self.get_12306_element()
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(element, location[0], location[1]).click().perform()
            time.sleep(1)

    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginSub')))
        submit.click()
        time.sleep(10)

    def check_login_success(self):
        """
        检查是否登录成功
        :return: None
        """
        success = False
        try:
            # 登录成功后的页面是找不到loginSub这个元素的。
            self.browser.find_element_by_id('loginSub')
            self.chaojiying.report_error(self.pic_id)
        except NoSuchElementException:
            success = True
        return success

    def crack(self):
        """
        破解入口
        :return: None
        """
        self.open()

        # 获取验证码图片
        image = self.get_12306_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')

        # 识别验证码
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        self.pic_id = result.get('pic_id')
        print(result)
        locations = self.get_points(result)
        self.touch_click_words(locations)

        # 登录
        self.login()

        # 失败后重试
        success = self.check_login_success()
        if not success:
            self.crack()
        else:
            print('登录成功')

if __name__ == '__main__':
    crack = Crack12306()
    crack.crack()