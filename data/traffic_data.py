import pandas as pd
import os
def get_feature_list(file_path:str):
    """
        获取数据集特征名称
        param:
            file_path: 数据集文件路径
        return:
            features_name: 特征名称列表(string)
    """
    try:
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
    except Exception as e:
        print(f"Error get_feature_list: {e}")
        # 重新读取文件
        return ""


def get_dataset_file_ext(file_path:str):
    """
        获取数据集文件后缀
        param:
            file_path: 数据集文件路径
        return:
            file_ext: 文件后缀
    """
    # 读取文件前几行判断文件格式
    try:
        with open(file_path, 'r') as f:
            first_lines = ''.join([f.readline() for _ in range(5)])
            
        # 判断是否为JSON格式
        if first_lines.strip().startswith('{') or first_lines.strip().startswith('['):
            # 判断是否为JSONL格式
            if '\n{' in first_lines:
                return '.jsonl'
            return '.json'
            
        # 判断是否为CSV格式(包含逗号分隔)
        if ',' in first_lines:
            return '.csv'
            
        # 判断是否为TXT格式
        if first_lines.strip():
            return '.txt'
            
        return os.path.splitext(file_path)[1]
            
    except:
        # 如果读取失败,返回文件名后缀
        return ".csv"

  
