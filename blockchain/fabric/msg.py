"""
    签名或不签名的消息结构定义
"""
#获取随机数消息
nonce_msg = {
    "user_id": "", #用户ID
    "tx_signature": b"" #交易签名(Base64 ASN.1 DER)
}

# 用户注册消息(不需要签名)
user_register_msg = {
    "user_name": "",  # 用户名称(可为空)
    "public_key": ""  # 用户公钥(pem string)
}

# 交易消息基础结构(需要签名)
tx_msg = {
    "user_id": "",           # 用户ID
    "tx_data": b"",          # 交易数据(Json bytes)
    "nonce": "",            # 随机数(base64)
    "tx_signature": b"",     # 交易签名(Base64 ASN.1 DER)
    "nonce_signature": b""   # 随机数签名(Base64 ASN.1 DER)
}

# 情报交易数据结构
cti_tx_data = {
    "cti_id": "",           # 情报ID
    "cti_name": "",         # 情报名称
    "cti_traffic_type": 0,  # 流量情报类型
    "open_source": 0,       # 是否开源
    "tags": [],            # 情报标签
    "iocs": [],            # 情报IOCs
    "statistic_info": b"",  # 统计信息
    "stix_data": b"",      # STIX数据
    "description": "",     # 情报描述
    "data_size": 0,        # 数据大小
    "ipfs_hash": "",       # IPFS地址
    "need": 0,             # 情报需求量
    "value": 0,            # 情报价值
    "compre_value": 0      # 综合价值
}

# 购买情报交易数据结构
purchase_cti_tx_data = {
    "cti_id": "",    # 情报ID
    "user_id": ""    # 用户ID
}

# 模型交易数据结构
model_tx_data = {
    "model_id": "",           # 模型ID
    "model_hash": "",         # 模型hash
    "model_name": "",         # 模型名称
    "model_type": 0,          # 模型类型
    "model_traffic_type": 0,  # 流量模型类型
    "model_open_source": 0,   # 是否开源
    "model_features": [],     # 模型特征
    "model_tags": [],         # 模型标签
    "model_description": "",  # 模型描述
    "model_data_size": 0,     # 数据大小
    "model_ipfs_hash": ""     # IPFS地址
}
