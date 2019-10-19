from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


url = 'https://login.taobao.com/member/login.jhtml'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2, 'notifications': 2}})  # chrome浏览器禁用加载图片，禁用弹窗

browser = webdriver.Chrome(options=chrome_options)
browser.set_window_size(1400, 700)

# 显示等待
wait = WebDriverWait(browser, 10)
browser.get(url)

'''
在F12开发者工具中，如果想要获取选择器name，可以直接在标签右键copy selector

.qrcode-login > .login-links > .forget-pwd'
'.' 表示class；'>' 表示进入。 就是从class=grcode-login这个节点进入下一个节点

#pl_login_logged > div > div:nth-child(2) > div > input'
'#' 表示id； div:nth-child(2)表示查找nth-child父元素的第2个子元素，即div标签下的第2个子标签。
'''

username = '请输入你的账号'
password = '请输入你的密码'


def login_taobao():
    url = 'https://s.taobao.com/search?q='
    # 获取'密码登录'按钮并点击
    # 在 10 秒内如果 指定的CSS选择器值（即密码登录按钮）成功加载出来，就返回该节点；如果超过 10 秒还没有加载出来，就抛出异常。
    # password_login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
    # password_login.click()

    # 获取'微博登录'按钮并点击
    weibo_login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
    weibo_login.click()

    # 获取'账号输入框'并输入账号
    EMAIL = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(2) > div > input')))
    EMAIL.send_keys(username)

    # 获取'密码输入框'并输入账号
    PASSWD = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(3) > div > input')))
    PASSWD.send_keys(password)

    # 获取'登录'按钮并点击
    button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a > span')))
    button.click()

    # 获取用户名并打印
    taobao_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                             '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
    print(taobao_name.text)
    return url


if __name__ == '__main__':
    login_taobao()