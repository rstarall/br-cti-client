import pandas as pd
from db.tiny_db import get_tiny_db_instance
from utils.file import get_file_sha256_hash
import os
def get_traffic_data_features_name(file_path:str):
    """
        获取流量数据集特征名称
        param:
            file_path: 数据集文件路径
        return:
            features_name: 特征名称列表
    """
    #判断后缀,csv or xlsx
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        return ValueError(f"file {file_path} is not a csv or xlsx file")
    #处理成字符串格式;分割
    features_name = ";".join(list(df.columns))
    return features_name


def record_stix_info_to_local_db(file_hash:str,output_file_path:str,stix_info=None):
    """
        将STIX记录写入本地数据库
        param:
            file_hash: 文件hash
            output_file_path: 输出文件路径
            record: STIX记录信息
    """
    new_stix_inforecord = {
        "file_hash":file_hash,
        "stix_file_path":"",
        "stix_file_size":0,#单位：字节
        "stix_file_hash":"",
        "stix_type":"",
        "stix_tags":"",
        "stix_iocs":"",
        "ioc_ips_map":{},
        "ioc_locations_map":{},
    }
    #判断file_path是否存在
    if  os.path.exists(output_file_path):
       new_stix_inforecord["stix_file_path"] = output_file_path
       new_stix_inforecord["stix_file_size"] = os.path.getsize(output_file_path)
       new_stix_inforecord["stix_file_hash"] = get_file_sha256_hash(output_file_path)
    if stix_info is not None:
        new_stix_inforecord["stix_type"] = stix_info["stix_type"]
        new_stix_inforecord["stix_tags"] = stix_info["stix_tags"]
        new_stix_inforecord["stix_iocs"] = stix_info["stix_iocs"]
    #处理ioc_ips_map
    if "ioc_ips_map" in stix_info:
        new_stix_inforecord["ioc_ips_map"] = stix_info["ioc_ips_map"]
    #处理ioc_locations_map
    if "ioc_locations_map" in stix_info:
        new_stix_inforecord["ioc_locations_map"] = stix_info["ioc_locations_map"]

    
    tiny_db = get_tiny_db_instance()
    #更新或插入数据(stix处理信息表)
    tiny_db.upsert_by_key_value("stix_info_record",new_stix_inforecord,"file_hash",file_hash)
    return True
