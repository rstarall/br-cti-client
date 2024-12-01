import ipaddress
import requests


def ip_to_location(ip:str):
    """
    判断传入的ip地址是否为公网地址，是则返回对应的实际地理位置，否则返回标注“内网”
    :param ip:IP地址
    :return:实际地理位置或内网标注
    """
    # 验证ip地址是否有效
    try:
        ip_object = ipaddress.ip_address(ip)
    except ValueError:
        print(f"error：{ip} 不是一个有效的IP地址！")
        return {"status": "error", "message": f"{ip} 不是一个有效的IP地址！"}

    # 私有地址
    if ip_object.is_private:
        print(f"{ip} 是私有地址")
        return {"status": "private", "message": f"{ip} 是私有地址"}

    # 公网地址返回实际地理位置
    try:
        access_token = "your token"  # ipinfo.io 官网注册获得的免费token
        url = f"https://ipinfo.io/{ip}/json?token={access_token}"  # 构造调用ip-api服务的url，并设置返回数据为json格式
        response = requests.get(url, timeout=5)  # 发送请求，设置超时时间为5秒
        response_data = response.json()  # 将返回数据转换成字典
        # 调用服务成功，返回地理信息
        if response.status_code == "200":
            location = {
                "status": "success",
                "country": response_data.get('country', '未知'),
                "region": response_data.get('region', '未知'),
                "city": response_data.get('city', '未知')
            }
            print(f"{ip} 对应地理位置信息：{location}")
            return location

        # 调用服务失败，打印报错信息
        else:
            print(f"{ip} 调用查询服务失败，状态代码：{response.status_code}")
            return {"status": "fail", "message": f"{ip} 调用查询服务失败：{response_data.get('Error', '未知错误')}"}

    except Exception as e:
        print(f"{ip} 查询地理位置时出错！error：{e}")
        return f"{ip} 查询地理位置时出错！error：{e}"


# 模块测试
if __name__ == "__main__":
    output = []  # 结果
    # 测试用例
    ip_test = [
        "202.192.80.55",
        "4564561.15362123",
        "192.168.0.238",
        "185.36.81.33",
        "192.168.0.238",
        "95.214.55.115",
        "154.209.125.131",
        "192.168.0.238",
        "103.203.57.7"
    ]
    for ip in ip_test:
        res = ip_to_location(ip)
        output.append(res)
    print(output)