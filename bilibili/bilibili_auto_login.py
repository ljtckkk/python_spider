from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO

THRESHOLD = 60
LEFT = 60
BORDER = 6
chrome_options = webdriver.ChromeOptions()
# 添加启动参数
chrome_options.add_argument("--window-size=1366,768")

USERNAME = "请输入用户名"
PASSWORD = "请输入密码"


class CrackGeeTest:
    def __init__(self):
        self.url = "https://passport.bilibili.com/login"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = USERNAME
        self.password = PASSWORD

    # 1. 在主动删除对象时触发__del__(self), 然后再删除对象自己。
    # 2. 如果对象没有删除，程序结束时，会自动删除对象。
    def __del__(self):
        print("关闭浏览器")
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        # 找到用户名输入框元素
        username = self.wait.until(
            EC.presence_of_element_located((By.ID, "login-username"))
        )
        # 找到密码输入框元素
        password = self.wait.until(
            EC.presence_of_element_located((By.ID, "login-passwd"))
        )
        # 发送账号到输入框元素
        username.send_keys(self.username)
        # 发送密码到输入框元素
        password.send_keys(self.password)

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return:
        """
        # 找到登录按钮元素
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))
        return button

    def get_geetest_image(self, name, full):
        """
        获取验证码图片
        :return: 图片对象
        """
        # 获取验证码图片 上下左右 坐标点
        top, bottom, left, right, size = self.get_position(full)
        print("验证码位置", top, bottom, left, right)
        # 屏幕截图
        screenshot = self.get_screenshot()
        # crop():从图像中提取出某个矩形大小的图像。它接收一个四元素的元组作为参数，各元素为(left, upper, right, lower),坐标系统的原点(0, 0)是左上角。
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)  # 保存图片
        return captcha

    def get_position(self, full):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        #
        img = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "geetest_canvas_bg"))
        )
        fullbg = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "geetest_canvas_fullbg"))
        )
        time.sleep(2)

        if full:
            # 使用js改变元素的属性值使之展示出来。把style属性值设置为"display:block。用于显示完整的图
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])",
                fullbg,
                "style",
                "display: block",
            )
        else:
            # 使用js改变元素的属性值使之展示出来。把style属性值设置为"display:none。用于显示有缺口的图（默认就是带缺口的）
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])",
                fullbg,
                "style",
                "display: none",
            )
        # location属性可以返回该图片对象(既这张图片)在浏览器中的位置，以字典的形式返回{‘x’:30, ‘y’:30}
        location = img.location
        # size属性同样返回图片对象的高度，宽度,以字典的形式返回{‘height’:30, ‘width’:30}
        size = img.size
        # 获取图片 上下左右 四个角的具体坐标点
        top, bottom, left, right = (
            location["y"],
            location["y"] + size["height"],
            location["x"],
            location["x"] + size["width"],
        )
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        # 遍历两张图片的每个像素，利用is_pixel_equal()方法判断两张图片同一位置的像素是否相同。比较两张图RGB的绝对值是否均小于定义的阈值threshold。
        # 如果绝对值均在阈值之内，则代表像素点相同，继续遍历。否则代表不相同的像素点，即缺口的位置。
        for i in range(LEFT, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    return i
        return LEFT

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if (
            abs(pixel1[0] - pixel2[0]) < THRESHOLD
            and abs(pixel1[1] - pixel2[1]) < THRESHOLD
            and abs(pixel1[2] - pixel2[2]) < THRESHOLD
        ):
            return True
        else:
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        distance += 20
        # 移动轨迹
        forward_tracks = []
        # 减速阈值
        mid = distance * 4 / 5
        # 当前位移
        current = 0
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3

            v0 = v
            v = v0 + a * t
            x = v0 * t + 0.5 * a * t * t
            current += x
            forward_tracks.append(round(x))

        backward_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        return {"forward_tracks": forward_tracks, "backward_tracks": backward_tracks}

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        button = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "geetest_slider_button"))
        )
        return button

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        # 调用ActionChains的click_and_hold()方法按住拖动底部滑块，遍历运动轨迹获取每小段位移距离，
        # 调用move_by_offset()方法移动此位移，最后调用release()方法松开鼠标即可。
        ActionChains(self.browser).click_and_hold(slider).perform()

        for x in track["forward_tracks"]:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()

        time.sleep(0.5)

        for x in track["backward_tracks"]:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()

        ActionChains(self.browser).release().perform()

    def crack(self):
        # 输入用户名密码
        self.open()
        # 点击验证按钮
        button = self.get_geetest_button()
        button.click()
        # 获取验证码完整图片
        image1 = self.get_geetest_image("captcha1.png", True)
        # 获取验证码缺口图片
        image2 = self.get_geetest_image("captcha2.png", False)
        # 获取缺口位置
        gap = self.get_gap(image1, image2)
        print("缺口位置", gap)
        # 减去缺口位移
        gap -= BORDER
        # 获取移动轨迹
        track = self.get_track(gap)
        print("滑动轨迹", track)
        # 获取移动轨迹
        slider = self.get_slider()
        # 拖动滑块
        self.move_to_gap(slider, track)
        time.sleep(1)

        try:
            self.wait.until(
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "geetest_panel_success_title"), "通过验证"
                )
            )
            print("成功登录！")
        except Exception:
            self.crack()


if __name__ == "__main__":
    crack = CrackGeeTest()
    crack.crack()
