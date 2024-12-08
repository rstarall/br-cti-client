import pandas as pd
from db.tiny_db import get_tiny_db_instance
from utils.file import get_file_sha256_hash
import os
def get_feature_list(file_path:str):
    """
        获取数据集特征名称
        param:
            file_path: 数据集文件路径
        return:
            features_name: 特征名称列表(string)
    """
    # 判断后缀,csv or xlsx or txt or json or jsonl,不同后缀做不同的读取方式
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    elif file_path.endswith(".txt"):
        df = pd.read_json(file_path,lines=True)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    elif file_path.endswith(".jsonl"):
        df = pd.read_json(file_path,lines=True)
    else:
        return ValueError(f"file {file_path} is not a csv or xlsx or txt or json or jsonl file")
    # 处理成字符串格式;分割
    features_name = ";".join(list(df.columns))
    return features_name


  
