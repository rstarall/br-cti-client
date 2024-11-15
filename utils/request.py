
"""
    定义发送HTTP或JSONRpc请求工具函数
"""
import json
import requests
def request_post(url, data):
    """
    发送POST请求
    :param url: 请求地址
    :param data: 请求数据
    :return: 返回结果 JSON 对象
    """
    try:
        # 发送 HTTP POST 请求
        response = requests.post(url, data)  
        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 数据
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response content: {response.content}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return 





def request_get(url):
    """
    发送GET请求
    :param url: 请求地址
    :return: 返回结果 JSON 对象
    """
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url)
        
        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 数据
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response content: {response.content}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")