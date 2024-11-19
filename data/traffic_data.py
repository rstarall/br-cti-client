import pandas as pd

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
