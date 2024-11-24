# 模型类型常量
MODEL_TYPE = {
    "TRAFFIC": 1,    # 恶意流量
    "MALWARE": 2,    # 恶意软件
    "PHISHING": 3,   # 钓鱼地址
    "BOTNET": 4,     # 僵尸网络
    "APP_LAYER": 5,  # 应用层攻击
}
MODEL_TYPE_NAME = {
    MODEL_TYPE["TRAFFIC"]: "恶意流量",
    MODEL_TYPE["MALWARE"]: "恶意软件", 
    MODEL_TYPE["PHISHING"]: "钓鱼地址",
    MODEL_TYPE["BOTNET"]: "僵尸网络",
    MODEL_TYPE["APP_LAYER"]: "应用层攻击"
}
# 流量模型类型常量
MODEL_TRAFFIC_TYPE = {
    "5G": 1,         # 5G
    "SATELLITE": 2,  # 卫星网络
    "SDN": 3         # SDN
}
MODEL_TRAFFIC_TYPE_NAME = {
    MODEL_TRAFFIC_TYPE["5G"]: "5G",
    MODEL_TRAFFIC_TYPE["SATELLITE"]: "卫星网络",
    MODEL_TRAFFIC_TYPE["SDN"]: "SDN"
}

# 示例数据
TRAFFIC_TYPE_LIST = ['卫星网络','SDN网络','5G网络','恶意软件','DDoS','钓鱼','僵尸网络','APT','IOT']
ML_TYPE_LIST = ['XGBoost','LightGBM','CatBoost','RandomForest','SVM','KNN','DecisionTree','NaiveBayes','GradientBoosting','AdaBoost']
TRAFFIC_FEATURES_LIST = [
    'dst_ip,src_ip,dst_port,src_port,proto,duration,bytes,packets',
]

model_info_example = {
    "model_id": "",  # 模型ID
    "model_hash": "", # 模型哈希
    "model_name": "", # 模型名称
    "model_type": 0, # 模型类型
    "model_traffic_type": 0, # 流量模型类型
    "model_open_source": 0, # 是否开源
    "model_features": [], # 模型特征
    "model_tags": [], # 模型标签
    "model_description": "", # 模型描述
    "model_data_size": 0, # 数据大小
    "model_ipfs_hash": "", # IPFS地址
    "create_time": "", # 创建时间
}