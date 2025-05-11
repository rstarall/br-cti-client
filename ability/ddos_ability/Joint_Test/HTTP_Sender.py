import requests
import json

# HTTP客户端函数
def HTTP_Client(url: str, data: dict):
    # 将数据转换为JSON字符串
    json_data = json.dumps(data)
    print(json_data)
    
    # 发送POST请求，包含JSON数据
    response = requests.post(url, json=data)  # 注意这里我们直接使用json=data参数，requests会自动处理编码
    
    # 检查响应状态码
    if response.status_code == 200:
        # 打印响应内容
        print(response.json())  # 假设服务器返回的是JSON格式的响应
    else:
        print(f"请求失败，状态码：{response.status_code}")

if __name__ == "__main__":
    # 要发送的JSON数据
    data = {
        "sid_rev": "active_defense_subsystem",
        "src": "10.2.87.12",  # 源IP
        "dst": "10.10.128.23",  # 目标IP
        "alarm": "dos",  # 告警内容
        "level": "2",  # 风险等级: 1, 2, 3
        "timestamp": "2024-5-18 15:12:18",  # 发现时间
        "defense_id": ["active_defense_subsyste_01"],  # 01: 端口跳变，02：IP跳变，03：流量牵引
        "other": {
            "rule": "TCP",  # 协议
        }
    }
    
    # 服务器URL（这里应该替换为实际的服务器地址）
    # 注意：由于这是一个HTTP客户端，我们需要一个完整的URL，包括协议（http或https）和可能的路径
    URL = "http://127.0.0.1:9998/api/endpoint"  # 这里的"/api/endpoint"应该替换为服务器实际接收POST请求的端点
    
    # 调用HTTP客户端函数
    HTTP_Client(URL, data)