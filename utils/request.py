
"""
    定义发送HTTP或JSONRpc请求工具函数
"""
import requests
def POST(url, data):
    """
    发送POST请求
    :param url: 请求地址
    :param data: 请求数据
    :return: 返回结果
    """
    return requests.post(url, data)

def GET(url):
    """
    发送GET请求
    :param url: 请求地址
    :return: 返回结果
    """
    return requests.get(url)