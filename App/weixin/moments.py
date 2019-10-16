from appium import webdriver
from pymongo import MongoClient
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from processor import Processor
from config import *


class Moments():
    def __init__(self):
        """初始化"""
        # 驱动配置
        self.desired_caps = {
            'platformName': PLATFORM,
            'deviceName': DEVICE_NAME,
            'appPackage': APP_PACKAGE,
            'appActivity': APP_ACTIVITY,
            'noReset': True,            # 启动后结束后不清空应用数据，用例执行完后会默认重置APP，也就是删除APP所有数据。
        }
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

        # 处理时间
        self.processor = Processor()

    def login(self):
        # 登录按钮
        login = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/emh')))
        login.click()
        # 手机输入
        phone = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/m6')))
        phone.set_text(USERNAME)
        # 下一步
        next = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/b2d')))
        next.click()
        # 密码
        password = self.wait.until(EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.LinearLayout[2]/android.widget.EditText')))
        # password = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="selectedElementContainer"]/div/div[2]/div/div[4]/div/div/div/div/div/div/table/tbody/tr[5]/td[2]')))
        password.set_text(PASSWORD)
        # 提交
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/b2d')))
        submit.click()

    def enter(self):
        # 选项卡
        tab = self.wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@content-desc=\"当前所在页面,与的聊天\"]/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[1]/android.widget.FrameLayout/android.widget.FrameLayout/com.tencent.mm.ui.mogic.WxViewPager/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ListView/android.widget.LinearLayout[11]/android.widget.LinearLayout')))
        tab.click()
        # 朋友圈
        moments = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ak0')))
        moments.click()

    def crawl(self):
        while True:
            # 上滑
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y)

            # 当前页面显示的所有状态
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@resource-id="com.tencent.mm:id/eyx"]//android.widget.FrameLayout')))
            # 遍历每条状态
            for item in items:
                try:
                    # 昵称
                    nickname = item.find_element_by_id('com.tencent.mm:id/bag').get_attribute('text')
                    # 正文
                    content = item.find_element_by_id('com.tencent.mm:id/f3p').get_attribute('text')
                    # 日期,android 7.0后无法看见
                    date = item.find_element_by_id('com.tencent.mm:id/eyd').get_attribute('text')
                    # 处理日期
                    date = self.processor.date(date)
                    print(nickname, content, date)
                    data = {
                        'nickname': nickname,
                        'content': content,
                        'date': date,
                    }
                    # 插入MongoDB
                    self.collection.update_one({'nickname': nickname, 'content': content}, {'$set': data}, True)
                except NoSuchElementException:
                    pass

    def main(self):
        """
        入口
        :return:
        """
        # 登录，仅第一次登录需要，如果手机微信已经登录，也不需要此方法
        # self.login()

        # 进入朋友圈
        self.enter()
        # 爬取
        self.crawl()

if __name__ == '__main__':
    moments = Moments()
    moments.main()



