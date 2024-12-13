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
    # 尝试不同的编码格式
    encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # 读取前3行进行格式判断
                first_lines = ''.join([f.readline() for _ in range(3)])
                
                # 判断是否为二进制文件
                if '\x00' in first_lines:
                    # Excel文件
                    if file_path.endswith(('.xls','.xlsx')):
                        return os.path.splitext(file_path)[1]
                    continue
                    
                # 判断是否为JSON格式
                if first_lines.strip().startswith('{') or first_lines.strip().startswith('['):
                    # 判断是否为JSONL格式
                    if '\n{' in first_lines:
                        return '.jsonl'
                    return '.json'
                
                # 判断是否为CSV格式(包含逗号分隔)
                if ',' in first_lines and not first_lines.strip().startswith('<'):
                    return '.csv'
                    
                # 判断是否为Excel格式
                if file_path.endswith(('.xls','.xlsx')):
                    return os.path.splitext(file_path)[1]
                    
                # 其他文本格式
                if first_lines.strip():
                    return '.txt'
                    
                return os.path.splitext(file_path)[1]
                
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"使用编码{encoding}读取文件时出错: {str(e)}")
            continue
            
    # 如果所有编码都失败,返回文件原始后缀
    print(f"无法判断文件格式,使用原始后缀")
    return os.path.splitext(file_path)[1]

