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
        return f"error：{ip} 不是一个有效的IP地址！"

    # 私有地址
    if ip_object.is_private:
        print(f"{ip} 是私有地址")
        return f"{ip} 是私有地址"

    # 公网地址返回实际地理位置
    try:
        url = f"http://ip-api.com/json/{ip}"  # 构造调用ip-api服务的url，并设置返回数据为json格式（免费的查询服务只能用http）
        response = requests.get(url, timeout=5)  # 发送请求，设置超时时间为5秒
        response_data = response.json()
        # 调用服务成功，返回地理信息
        if response_data["status"] == "success":
            print(f"{ip} 对应地理位置：{response_data['country']}, {response_data['regionName']}, {response_data['city']}")
            return f"{ip} 对应地理位置：{response_data['country']}, {response_data['regionName']}, {response_data['city']}"

        # 调用服务失败，打印报错信息
        elif response_data["status"] == "fail":
            print(f"{ip} 调用查询服务失败：{response_data['message']}")
            return f"{ip} 调用查询服务失败：{response_data['message']}"

    except Exception as e:
        print(f"{ip} 查询地理位置时出错！error：{e}")
        return f"{ip} 查询地理位置时出错！error：{e}"


def ips_to_location(ips:dict):
    """
        将ip字典转换为地理位置字典
        param:
            ips: 字典(ip->ip出现数量)
        return:
            ip_location_map: 字典(ip->地理位置)
            location_num_map: 字典(地理位置->位置出现数量)
    """
    ip_location_map = {}
    location_num_map = {}
    for ip,ip_num in ips.items():
        location = ip_to_location(ip)
        ip_location_map[ip] = location
        location_num_map[location] = location_num_map.get(location,0)+ip_num
    return ip_location_map,location_num_map


# 模块测试
def test_ip_to_location():
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





