import ipaddress
import requests
import threading
import random
access_token = "0962796833d3d6f21eda2234b1e1bb5e"  # ipinfo.io 官网注册获得的免费token
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
        url = f"https://ipinfo.io/{ip}/json?token={access_token}"  # 构造调用ip-api服务的url，并设置返回数据为json格式
        response = requests.get(url, timeout=5)  # 发送请求，设置超时时间为5秒
        response_data = response.json()  # 将返回数据转换成字典
        # 调用服务成功，返回地理信息
        if response_data["status"] == "success":
            print(f"{ip} 对应地理位置：{response_data['country']}, {response_data['regionName']}, {response_data['city']}")
            return f"{response_data['country']},{response_data['regionName']},{response_data['city']}"

        # 调用服务失败，打印报错信息
        elif response_data["status"] == "fail":
            print(f"{ip} 调用查询服务失败：{response_data['message']}")
            return ""
        # 调用服务失败，打印报错信息
        else:
            print(f"{ip} 调用查询服务失败，状态代码：{response.status_code}")
            return {"status": "fail", "message": f"{ip} 调用查询服务失败：{response_data.get('Error', '未知错误')}"}

    except Exception as e:
        print(f"{ip} 查询地理位置时出错！error：{e}")
        return ""


def ips_to_location(ips:dict):
    """
        将ip字典转换为地理位置字典
        param:
            ips: 字典(ip->ip出现数量)
        return:
            ip_location_map: 字典(ip->地理位置)
            location_num_map: 字典(地理位置->位置出现数量)
            errors: 错误信息列表
    """
    ip_location_map = {}
    location_num_map = {}
    errors = [] 
    for index,(ip,ip_num) in enumerate(ips.items()):
        print(f"正在处理ip:{ip}({index}/{len(ips.keys())})")
        try:
            location = ip_to_location(ip)   
        except Exception as e:
            errors.append(f"ip_to_location error:{e}")
            continue
        ip_location_map[ip] = location
        location_num_map[location] = location_num_map.get(location,0)+ip_num
    return ip_location_map,location_num_map,errors
def ips_to_location_mock_random(ips:dict):
    """
        将IP地址随机转换为地理位置
        param:
            ips: 字典(ip->ip出现数量)
        return:
            ip_location_map: 字典(ip->地理位置)
            location_num_map: 字典(地理位置->位置出现数量)
            errors: 错误信息列表
    """
    ip_location_map = {}
    location_num_map = {}
    errors = []
    
    # 模拟的地理位置列表
    locations = [
        "中国,北京,北京",
        "中国,上海,上海", 
        "中国,广东,深圳",
        "美国,加利福尼亚,旧金山",
        "日本,东京,东京",
        "韩国,首尔,首尔",
        "英国,伦敦,伦敦",
        "德国,柏林,柏林",
        "法国,巴黎,巴黎",
        "俄罗斯,莫斯科,莫斯科"
    ]
    
    for ip, ip_num in ips.items():
        # 随机选择一个地理位置
        location = random.choice(locations)
        ip_location_map[ip] = location
        location_num_map[location] = location_num_map.get(location, 0) + ip_num
        
    return ip_location_map, location_num_map, errors

def ips_to_location_concurrent(ips:dict, max_workers=100):
    """
        使用多线程并发将ip字典转换为地理位置字典
        param:
            ips: 字典(ip->ip出现数量)
            max_workers: 最大线程数,默认10
        return:
            ip_location_map: 字典(ip->地理位置)
            location_num_map: 字典(地理位置->位置出现数量) 
            errors: 错误信息列表
    """
    ip_location_map = {}
    location_num_map = {}
    errors = []
    threads = []
    results = {}
    
    def process_ip(ip, ip_num):
        try:
            location = ip_to_location(ip)
            results[ip] = (location, ip_num, None)
        except Exception as e:
            results[ip] = (None, ip_num, f"ip_to_location error:{e}")
            
    # 创建并启动线程
    for index, (ip, ip_num) in enumerate(ips.items()):
        while len(threads) >= max_workers:
            for t in threads[:]:
                if not t.is_alive():
                    threads.remove(t)
                    
        thread = threading.Thread(target=process_ip, args=(ip, ip_num))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        print(f"启动处理:{index + 1}/{len(ips.keys())}")
        
    # 等待所有线程完成
    for t in threads:
        t.join()
        
    # 处理结果
    for ip, (location, ip_num, error) in results.items():
        if error:
            errors.append(error)
            continue
            
        ip_location_map[ip] = location
        location_num_map[location] = location_num_map.get(location, 0) + ip_num
            
    return ip_location_map, location_num_map, errors

def ips_to_location_bulk(ips: dict, batch_size=30):
    """
    使用批量查询API将IP地址转换为地理位置信息
    param:
        ips: 字典(ip->ip出现数量)
        batch_size: 每批次查询的IP数量,默认30个
    return:
        ip_location_map: 字典(ip->地理位置)
        ip_location_info_map: 字典(ip->地理位置详细信息)
        location_num_map: 字典(地理位置->位置出现数量)
        errors: 错误信息列表
    """
    ip_location_map = {}
    ip_location_info_map = {}
    location_num_map = {}
    errors = []
    
    # 将IP地址列表分批
    ip_list = list(ips.keys())
    for i in range(0, len(ip_list), batch_size):
        batch_ips = ip_list[i:i + batch_size]
        
        # 构建批量查询URL
        ips_param = ','.join(batch_ips)
        url = f"https://api.ipinfo.io/api/{ips_param}?access_key={access_token}"
        
        try:
            # 发送GET请求进行批量查询
            response = requests.get(url, timeout=10)
            response_data = response.json()
            
            # 处理每个IP的响应结果
            for ip_data in response_data:
                ip = ip_data.get('ip')
                print(f"正在处理ip:{ip}({i+1}/{len(ip_list)})")
                
                if "error" in ip_data:
                    errors.append(f"IP {ip} 查询失败: {ip_data['error']}")
                    continue
                    
                try:
                    # 存储完整的地理信息
                    location_info = {
                        'ip': ip_data.get('ip'),
                        'type': ip_data.get('type'),
                        'continent_code': ip_data.get('continent_code'),
                        'continent_name': ip_data.get('continent_name'),
                        'country_code': ip_data.get('country_code'),
                        'country_name': ip_data.get('country_name'),
                        'region_code': ip_data.get('region_code'),
                        'region_name': ip_data.get('region_name'),
                        'city': ip_data.get('city'),
                        'zip': ip_data.get('zip'),
                        'latitude': ip_data.get('latitude'),
                        'longitude': ip_data.get('longitude'),
                        'msa': ip_data.get('msa'),
                        'dma': ip_data.get('dma'),
                        'radius': ip_data.get('radius'),
                        'ip_routing_type': ip_data.get('ip_routing_type'),
                        'connection_type': ip_data.get('connection_type')
                    }
                    
                    # 简化的地理位置字符串
                    location_str = f"{ip_data.get('country_name', '')},{ip_data.get('region_name', '')},{ip_data.get('city', '')}"
                    
                    ip_location_map[ip] = location_str
                    ip_location_info_map[ip] = location_info
                    location_num_map[location_str] = location_num_map.get(location_str, 0) + ips[ip]
                    
                except Exception as e:
                    errors.append(f"处理IP {ip} 数据时出错: {str(e)}")
                    
        except Exception as e:
            errors.append(f"批量查询请求失败: {str(e)}")
            continue
            
    return ip_location_map, ip_location_info_map, location_num_map, errors







