

def ip_to_location(ip:str):
    """
        将ip地址转换为地理位置
        需要依赖外部接口或者IP地理数据库
    """
    pass


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
