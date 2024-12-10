import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import re
import numpy as np

def read_file_as_df(file_path):
    """
        读取文件为DataFrame
    """
    # 根据数据集不同的文件类型选择不同的读取方式
    try:
        file_suffix = os.path.splitext(file_path)[1]
        if file_suffix == ".csv":
            dataset = pd.read_csv(file_path)
        elif file_suffix == ".txt":
            dataset = pd.read_json(file_path, lines=True)
        elif file_suffix == ".xlsx":
            dataset = pd.read_excel(file_path)
        else:
            return None, "不支持的文件类型"
    except Exception as e:
        print(f"文件打开失败！：{e}")
        return None, f"文件打开失败！：{e}"
    # 添加检查
    if dataset.empty:
        return None, "数据集为空！"
    return dataset, None

def get_dict_depth(d):
    """
    获取字典的深度
    
    参数:
    - d: 待检查的字典
    
    返回:
    - depth: 字典的深度
    """
    if not isinstance(d, dict) or not d:
        return 0
    nested_dicts = [v for v in d.values() if isinstance(v, dict)]
    if not nested_dicts:  # 如果没有嵌套字典
        return 1
    return 1 + max(get_dict_depth(v) for v in nested_dicts)

def flatten_dict(df, max_depth=3):
    """
    展开数据框中的字典字段
    
    参数:
    - df: pandas DataFrame
    - max_depth: 最大展开深度，默认为3
    
    返回:
    - flattened_df: 展开后的DataFrame
    """
    def _flatten_dict_column(d, parent_key='', sep='_', current_depth=0):
        items = []
        if not isinstance(d, dict):
            return [(parent_key, d)]
        
        if current_depth >= max_depth:
            return [(parent_key, str(d))]
            
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and get_dict_depth(v) > 1:
                items.extend(_flatten_dict_column(v, new_key, sep, current_depth + 1))
            elif isinstance(v, list):
                # 处理列表：将列表转换为字符串或者提取第一个元素
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return items

    # 创建一个新的DataFrame来存储展开后的数据
    flattened_data = []
    
    # 遍历每一行
    for _, row in df.iterrows():
        flat_row = {}
        # 处理每一列
        for col in df.columns:
            value = row[col]
            if isinstance(value, dict) and get_dict_depth(value) > 1:
                # 只有当是字典且深度大于1时才展开
                flattened = dict(_flatten_dict_column(value))
                flat_row.update(flattened)
            else:
                # 保持非字典值或浅层字典不变
                flat_row[col] = value
        flattened_data.append(flat_row)
    
    # 创建新的DataFrame
    flattened_df = pd.DataFrame(flattened_data)
    
    return flattened_df

def clean_data(df, source_file_hash, output_folder):
    """
    清洗数据，包括展开字典字段
    """
    try:
        # # 展开字典字段
        # df = flatten_dict(df, max_depth=3)
        
        # 将所有字典类型的值转换为字符串
        for column in df.columns:
            df[column] = df[column].apply(lambda x: str(x) if isinstance(x, dict) else x)
        
        # 类型标准化
        df = standardize_data_types(df)
        
        # 删除重复行
        df = df.drop_duplicates()
        
        # 保存清洗后的数据
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        clean_file_path = os.path.join(output_folder, f"cleaned_{source_file_hash}.csv")
        df.to_csv(clean_file_path, index=False)
        
        return df, clean_file_path, None
        
    except Exception as e:
        print(f"数据清洗过程中发生错误: {str(e)}")
        return None, None, f"数据清洗失败: {str(e)}"



def standardize_data_types(df):
    """
    对数据框中的列进行数据类型标准化和编码转换
    """
    df = df.copy()
    
    # IP地址的正则表达式模式
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'

    def ip_to_int(ip):
        try:
            # 将 IP 地址转换为数值
            parts = list(map(int, str(ip).split('.')))
            if len(parts) != 4 or any(part < 0 or part > 255 for part in parts):
                return None
            return sum(part * (256 ** (3-i)) for i, part in enumerate(parts))
        except:
            return 0
        
    # 时间戳的正则表达式模式
    timestamp_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
        r'^\d{10}$',  # Unix timestamp
    ]
    
    categorical_columns = []
    
    def is_numeric_string(s):
        """检查字符串是否为数值"""
        try:
            float(str(s).replace(',', ''))
            return True
        except:
            return False

    for column in df.columns:
        sample_values = df[column].dropna().head().astype(str)
        
        try:
            # 1. 检查并处理IP地址
            if any(re.match(ip_pattern, str(val)) for val in sample_values):
                df[column] = df[column].apply(ip_to_int)
                
            # 2. 检查时间戳
            elif any(any(re.match(pattern, str(val)) for pattern in timestamp_patterns) 
                    for val in sample_values):
                try:
                    df[column] = pd.to_datetime(df[column])
                    df[column] = df[column].astype(np.int64) // 10**9
                except:
                    categorical_columns.append(column)
            
            # 3. 检查数值型数据
            elif df[column].dtype in ['int64', 'float64', 'int32', 'float32']:
                df[column] = df[column].fillna(0).astype('int64')
            
            # 4. 处理布尔值
            elif df[column].dtype == 'bool':
                df[column] = df[column].astype(int)
            
            # 5. 处理可能包含数值的字符串
            elif df[column].dtype == 'object':
                # 检查是否所有非空值都是数值字符串
                non_na_values = df[column].dropna()
                if len(non_na_values) > 0 and all(is_numeric_string(x) for x in non_na_values):
                    # 处理可能包含逗号的数值字符串
                    df[column] = df[column].apply(lambda x: float(str(x).replace(',', '')) if pd.notna(x) else np.nan)
                    df[column] = df[column].fillna(0).astype('int64')
                else:
                    # 处理非数值字符串
                    df[column] = df[column].replace(['null', 'none', 'nan', 'undefined', ''], pd.NA)
                    # 如果列中的唯一值数量过多（比如超过列长度的50%），可能是连续值而不是分类值
                    if len(df[column].unique()) < len(df) * 0.5:
                        categorical_columns.append(column)
                    else:
                        # 对于非分类的字符串列，使用哈希函数转换为数值
                        df[column] = df[column].apply(lambda x: hash(str(x)) % (2**32) if pd.notna(x) else 0)
                
        except Exception as e:
            print(f"处理列 {column} 时发生错误: {str(e)}")
            # 发生错误时使用哈希函数作为后备方案
            df[column] = df[column].apply(lambda x: hash(str(x)) % (2**32) if pd.notna(x) else 0)
            continue
    
    # 对分类特征进行标签编码
    if categorical_columns:
        for col in categorical_columns:
            # 使用标签编码替代独热编码，这样可以保持原始列名
            df[col] = pd.Categorical(df[col]).codes.astype('int64')
    
    # 最后确保所有列都是整型
    for col in df.columns:
        if df[col].dtype != 'int64':
            df[col] = df[col].fillna(0).astype('int64')
    
    return df
