"""
    保存数据结构
    CTI数据结构(链上)
"""

# 情报类型常量
CTI_TYPE = {
    "TRAFFIC": 1,    # 恶意流量 
    "HONEYPOT": 2,   # 蜜罐情报
    "BOTNET": 3,     # 僵尸网络
    "APP_LAYER": 4,  # 应用层攻击
    "OPEN_SOURCE": 5 # 开源情报
}
CTI_TYPE_NAME = {
    CTI_TYPE["TRAFFIC"]: "恶意流量",
    CTI_TYPE["HONEYPOT"]: "蜜罐情报",
    CTI_TYPE["BOTNET"]: "僵尸网络", 
    CTI_TYPE["APP_LAYER"]: "应用层攻击",
    CTI_TYPE["OPEN_SOURCE"]: "开源情报"
}
# 流量情报类型常量
CTI_TRAFFIC_TYPE = {
    "5G": 1,         # 5G
    "SATELLITE": 2,  # 卫星网络
    "SDN": 3         # SDN
}
CTI_TRAFFIC_TYPE_NAME = {
    CTI_TRAFFIC_TYPE["5G"]: "5G",
    CTI_TRAFFIC_TYPE["SATELLITE"]: "卫星网络",
    CTI_TRAFFIC_TYPE["SDN"]: "SDN"
}
# 示例数据
TAGS_LIST = {
    "honeypot": "蜜罐情报",
    "satellite": "卫星网络",
    "sdn": "SDN网络", 
    "5g": "5G网络",
    "malware": "恶意软件",
    "ddos": "DDoS",
    "phishing": "钓鱼",
    "botnet": "僵尸网络",
    "apt": "APT",
    "iot": "IOT",
    "other": "其他"
}
IOCS_LIST = {
    "ip": "IP地址",
    "port": "端口号", 
    "flow_feature": "流量特征",
    "hash": "哈希值",
    "url": "网址",
    "payload": "载荷"
}
cti_info_example = {
    "cti_hash":"", #情报hash值(情报结构体整体Sha256生成，不可与链上已有的情报重复)
    "cti_name":"", #情报名称
    "cti_type":0, #情报类型
    "cti_traffic_type":0, #情报流量类型
    "open_source":0, 
    "creator_user_id":"", #创建者用户ID
    "tags":[], #情报标签
    "iocs":[], #情报IOCs
    "satistic_info":{}, #情报统性信息(转成[]byte)
    "stix_data":{}, #STIX数据(转成[]byte)
    "description":"", #情报描述
    "data_size":0, #情报数据大小
    "data_hash":"", #情报数据哈希
    "ipfs_hash":"", #IPFS哈希
    "need":0, #情报需求
    "value":0, #情报价值(用户指定)
    "compre_value":0, #情报综合价值(平台评估)
    "create_time":"", #创建时间
}



