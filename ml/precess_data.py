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

def clean_data(df,file_hash, output_folder='./dataset'):
    """
        对数据集进行清洗
        param:
            - df: 输入数据集
            - file_hash: 文件的hash值
            - output_folder: 输出文件夹路径
        return:
            - df: 清洗后的数据集
            - output_file_path: 清洗后的数据集文件路径(统一为csv格式)
            - error: 错误信息
    """

    # 2. 去除空值
    df = df.dropna()

    # 3. 处理异常值
    threshold = 3
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numerical_columns:
        mean = df[col].mean()
        std = df[col].std()
        df = df[(df[col] >= mean - threshold * std) & (df[col] <= mean + threshold * std)]

    # 4. 删除重复行
    df = df.drop_duplicates()

    # 5. 创建保存目录（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 6. 保存清洗后的数据
    # 使用输入文件名创建输出文件路径
    output_file_path = os.path.join(output_folder, f"{file_hash}_cleaned.csv")
    df.to_csv(output_file_path, index=False)
    print(f"数据清洗完成并已保存至 {output_file_path}")
    return df,output_file_path, None

