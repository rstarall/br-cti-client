from db.tiny_db import get_tiny_db_instance
# 样例数据
example_attack_type_list = ['恶意流量', '恶意软件', '钓鱼地址', '僵尸网络', '应用层攻击', '开源情报']
example_tags_list = ['卫星网络', 'SDN网络', '5G网络', '恶意软件', 'DDoS', '钓鱼', '僵尸网络', 'APT', 'IOT']  # tags表示涉及的攻击技术
example_iocs_list = ['IP', '端口', '流特征', 'HASH', 'URL', 'CVE']  # iocs表示沦陷指标
client_data_table_instance = None
client_stix_data_list = [{
    "id": 1,
    "status": "处理中",
    "type": "恶意流量",
    "tags": "DDoS;卫星网络;",
    "iocs": "IP;端口;流特征;",
    "source_hash": "15cbac",
    "create_time": "2024-11-09",
    "onchain": "是"
}]
