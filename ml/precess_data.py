import pandas as pd
import os
from sklearn.preprocessing import StandardScaler

def clean_data(input_file, output_folder='./dataset'):

    # 1. 读取数据
    df = pd.read_csv(input_file)

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
    output_file = os.path.join(output_folder, f"cleaned_{os.path.basename(input_file)}")
    df.to_csv(output_file, index=False)
    print(f"数据清洗完成并已保存至 {output_file}")


# 示例：使用指定的文件名调用函数
if __name__ == '__main__':
    clean_data('./Test_dataset/dataset.csv')
