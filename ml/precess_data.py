import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
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
        # 展开字典字段
        df = flatten_dict(df, max_depth=3)
        
        # 将所有字典类型的值转换为字符串
        for column in df.columns:
            df[column] = df[column].apply(lambda x: str(x) if isinstance(x, dict) else x)
        
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
