# urllib代理==================================================================================================================
# ==================================================================================================================
# from urllib.error import URLError
# from urllib.request import ProxyHandler, build_opener

# proxy = 'username:password@127.0.0.1:9743'    # 需要认证的代理
# proxy = '127.0.0.1:9743'
# proxy_handler = ProxyHandler({
#     'http': 'http://' + proxy,
#     'https': 'https://' + proxy
# })
# opener = build_opener(proxy_handler)
# try:
#     response = opener.open('http://httpbin.org/get')
#     print(response.read().decode('utf-8'))
# except URLError as e:
#     print(e.reason)


# urllib socks代理，全局设置==================================================================================================================
# ==================================================================================================================
# import socks
# import socket
# from urllib import request
# from urllib.error import URLError
#
# socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 9742)
# socket.socket = socks.socksocket
# try:
#     response = request.urlopen('http://httpbin.org/get')
#     print(response.read().decode('utf-8'))
# except URLError as e:
#     print(e.reason)


# requests代理==================================================================================================================
# ==================================================================================================================
import requests
# proxy = 'username:password@127.0.0.1:9743'      # 需要认证的代理
proxy = '120.83.105.184:9999'
proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy,
}
try:
    response = requests.get('http://httpbin.org/get', proxies=proxies)
    print(response.text)
except requests.exceptions.ConnectionError as e:
    print('Error', e.args)


# requests socks代理==================================================================================================================
# ==================================================================================================================
# import requests
#
# proxy = '127.0.0.1:1080'
# proxies = {
#     'http': 'socks5://' + proxy,
#     'https': 'socks5://' + proxy
# }
# try:
#     response = requests.get('http://httpbin.org/get', proxies=proxies)
#     print(response.text)
# except requests.exceptions.ConnectionError as e:
#     print('Error', e.args)


# requests socks代理，全局设置==================================================================================================================
# ==================================================================================================================
# import requests
# import socks
# import socket
#
# socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 9742)
# socket.socket = socks.socksocket
# try:
#     response = requests.get('http://httpbin.org/get')
#     print(response.text)
# except requests.exceptions.ConnectionError as e:
#     print('Error', e.args)