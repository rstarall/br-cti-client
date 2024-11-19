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

class StixDataObject:
    def __init__(self, id: str,  created: str, ):
        self.id = id
        self.created = created
        self.data = None # 数据(json一条或多个，或者sha256)
    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "type": self._type,
            "tags": self.tags,
            "iocs": self.iocs,
            "source_hash": self.source_hash,
            "create_time": self.create_time,
            "onchain": self.onchain,
            "created": self.created
        }
    def save_to_local_db(self):
        tiny_db_instance = get_tiny_db_instance()
        tiny_db_instance.insert(self.to_dict())
        pass
    def set_status(self, status: str):
        self.status = status
    def set_type(self, _type: str):
        self._type = _type
    def set_tags(self, tags: str):
        self.tags = tags
    def set_iocs(self, iocs: str):
        self.iocs = iocs
    def set_source_hash(self, source_hash: str):
        self.source_hash = source_hash
    def set_create_time(self, create_time: str):
        self.create_time = create_time
    def set_onchain(self, onchain: str):
        self.onchain = onchain