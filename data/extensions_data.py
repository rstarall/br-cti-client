import ipaddress
import requests
import threading
import random
access_token = "0962796833d3d6f21eda2234b1e1bb5e"  # ipinfo.io 官网注册获得的免费token



def ips_to_location_mock_random(ips:dict):
    """
        将IP地址随机转换为地理位置
        param:
            ips: 字典(ip->ip出现数量)
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
        "俄罗斯,莫斯科,莫斯科",
        "加拿大,安大略,多伦多",
        "澳大利亚,新南威尔士,悉尼",
        "印度,马哈拉施特拉,孟买",
        "巴西,圣保罗,圣保罗",
        "新加坡,新加坡,新加坡",
        "意大利,拉齐奥,罗马",
        "西班牙,马德里,马德里"
    ]
    
    # 模拟的地理位置详细信息
    location_infos = {
        "中国,北京,北京": {"country":"CN","region":"Beijing","city":"Beijing","loc":"39.9075,116.3972"},
        "中国,上海,上海": {"country":"CN","region":"Shanghai","city":"Shanghai","loc":"31.2222,121.4581"},
        "中国,广东,深圳": {"country":"CN","region":"Guangdong","city":"Shenzhen","loc":"22.5431,114.0579"},
        "美国,加利福尼亚,旧金山": {"country":"US","region":"California","city":"San Francisco","loc":"37.7749,-122.4194"},
        "日本,东京,东京": {"country":"JP","region":"Tokyo","city":"Tokyo","loc":"35.6762,139.6503"},
        "韩国,首尔,首尔": {"country":"KR","region":"Seoul","city":"Seoul","loc":"37.5665,126.9780"},
        "英国,伦敦,伦敦": {"country":"GB","region":"England","city":"London","loc":"51.5074,-0.1278"},
        "德国,柏林,柏林": {"country":"DE","region":"Berlin","city":"Berlin","loc":"52.5200,13.4050"},
        "法国,巴黎,巴黎": {"country":"FR","region":"Île-de-France","city":"Paris","loc":"48.8566,2.3522"},
        "俄罗斯,莫斯科,莫斯科": {"country":"RU","region":"Moscow","city":"Moscow","loc":"55.7558,37.6173"},
        "加拿大,安大略,多伦多": {"country":"CA","region":"Ontario","city":"Toronto","loc":"43.6532,-79.3832"},
        "澳大利亚,新南威尔士,悉尼": {"country":"AU","region":"New South Wales","city":"Sydney","loc":"-33.8688,151.2093"},
        "印度,马哈拉施特拉,孟买": {"country":"IN","region":"Maharashtra","city":"Mumbai","loc":"19.0760,72.8777"},
        "巴西,圣保罗,圣保罗": {"country":"BR","region":"São Paulo","city":"São Paulo","loc":"-23.5505,-46.6333"},
        "新加坡,新加坡,新加坡": {"country":"SG","region":"Singapore","city":"Singapore","loc":"1.3521,103.8198"},
        "意大利,拉齐奥,罗马": {"country":"IT","region":"Lazio","city":"Rome","loc":"41.9028,12.4964"},
        "西班牙,马德里,马德里": {"country":"ES","region":"Madrid","city":"Madrid","loc":"40.4168,-3.7038"}
    }
    
    for ip, ip_num in ips.items():
        # 随机选择一个地理位置
        location = random.choice(locations)
        ip_location_map[ip] = location
        ip_location_info_map[ip] = location_infos[location]
        location_num_map[location] = location_num_map.get(location, 0) + ip_num
        
    return ip_location_map, ip_location_info_map, location_num_map, errors

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
    ip_location_info_map = {}
    location_num_map = {}
    errors = []
    threads = []
    results = {}
    
    def process_ip(ip, ip_num):
        try:
            location, location_info = ips_to_location_single(ip)
            results[ip] = (location,location_info, ip_num, None)
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
    for ip, (location, location_info, ip_num, error) in results.items():
        if error:
            errors.append(error)
            continue
            
        ip_location_map[ip] = location
        ip_location_info_map[ip] = location_info
        location_num_map[location] = location_num_map.get(location, 0) + ip_num
            
    return ip_location_map, ip_location_info_map, location_num_map, errors


def ips_to_location(ips:dict):
    """
    将ip字典转换为地理位置字典
    param:
        ips: 字典(ip->ip出现数量)
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
    
    for index,(ip,ip_num) in enumerate(ips.items()):
        print(f"正在处理ip:{ip}({index+1}/{len(ips)})")
        try:
            location_str, location_info = ips_to_location_single_2(ip)
            ip_location_map[ip] = location_str
            ip_location_info_map[ip] = location_info
            location_num_map[location_str] = location_num_map.get(location_str,0) + ip_num
        except Exception as e:
            errors.append(f"处理IP {ip} 失败: {str(e)}")
            print(f"处理IP {ip} 失败: {str(e)}")
            continue
            
    return ip_location_map, ip_location_info_map, location_num_map, errors



def ips_to_location_single(ip: str):
    """
    使用单次查询API将单个IP地址转换为地理位置信息
    param:
        ip: IP地址
    return:
        location_str: 地理位置字符串
        location_info: 地理位置详细信息字典
    """
    url = f"https://api.ipinfo.io/{ip}?token={access_token}"
    
    response = requests.get(url, timeout=10)
    ip_data = response.json()
    
    if "error" in ip_data:
        print(f"IP {ip} 查询失败: {url}")
        raise Exception(f"IP {ip} 查询失败: {ip_data['error']}")
        
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
    
    return location_str, location_info




def ips_to_location_single_2(ip: str):
    """
    使用ip-api.com的API将单个IP地址转换为地理位置信息
    param:
        ip: IP地址
    return:
        location_str: 地理位置字符串
        location_info: 地理位置详细信息字典
    """
    url = f"http://ip-api.com/json/{ip}"
    
    response = requests.get(url, timeout=10)
    ip_data = response.json()
    
    if ip_data.get("status") != "success":
        print(f"IP {ip} 查询失败: {url}")
        raise Exception(f"IP {ip} 查询失败: {ip_data.get('message', '未知错误')}")
        
    # 存储完整的地理信息
    location_info = {
        'ip': ip_data.get('query'),
        'country_code': ip_data.get('countryCode'),
        'country_name': ip_data.get('country'),
        'region_code': ip_data.get('region'),
        'region_name': ip_data.get('regionName'),
        'city': ip_data.get('city'),
        'zip': ip_data.get('zip'),
        'latitude': ip_data.get('lat'),
        'longitude': ip_data.get('lon'),
        'timezone': ip_data.get('timezone'),
        'isp': ip_data.get('isp'),
        'org': ip_data.get('org'),
        'as': ip_data.get('as')
    }
    
    # 简化的地理位置字符串
    location_str = f"{ip_data.get('country', '')},{ip_data.get('regionName', '')},{ip_data.get('city', '')}"
    
    return location_str, location_info


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
                    print(f"处理IP {ip} 数据时出错: {str(e)}")
                    
        except Exception as e:
            errors.append(f"批量查询请求失败: {str(e)}")
            print(f"批量查询请求失败: {str(e)}")
            print(f"批量查询请求失败: {url}")
            continue
            
    return ip_location_map, ip_location_info_map, location_num_map, errors
