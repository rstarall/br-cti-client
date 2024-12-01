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
TAGS_LIST = ["卫星网络", "SDN网络", "5G网络", "恶意软件", "DDoS", "钓鱼", "僵尸网络", "APT", "IOT"]
IOCS_LIST = ["IP", "端口", "流特征", "HASH", "URL", "payload"]
SATISTIC_INFO = {"location": {"中国":1,"美国":2,"俄罗斯":3,"英国":4,"法国":5,"德国":6,"日本":7,"韩国":8,"印度":9,"巴西":10}}

cti_info_example = {
    "cti_hash":"", #情报hash值(情报结构体整体Sha256生成，不可与链上已有的情报重复)
    "cti_name":"", #情报名称
    "cti_type":0, #情报类型
    "cti_traffic_type":0, #情报流量类型(5G、卫星网络、SDN)
    "open_source":0, #情报来源
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



