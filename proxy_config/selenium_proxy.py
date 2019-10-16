from selenium import webdriver

proxy = '113.65.5.6:8118'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=http://' + proxy)
browser = webdriver.Chrome(options=chrome_options)
browser.get('http://httpbin.org/get')
