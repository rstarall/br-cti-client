import joblib
import time
import numpy as np
import pandas as pd
from tinydb import TinyDB, Query
from sklearn.metrics import accuracy_score, mean_squared_error, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from db.tiny_db import TinyDBUtil
# 初始化 TinyDB 数据库
# 初始化 TinyDB 数据库
progress_table = TinyDBUtil().use_database('ml_process_progress').open_table('progress')


# 记录训练进度和评估信息
def log_progress(request_id,source_file_hash, stage, message, evaluate_results={}):
    """
        记录训练进度、评估信息和时间。
        如果相同请求ID已经存在记录，则覆盖记录。
        param:
            - request_id: 请求ID
            - source_file_hash: 数据源文件的hash值
            - stage: 阶段
            - message: 消息
            - evaluate_results: 评估结果
    """
    record = {
        'request_id': request_id,
        'source_file_hash': source_file_hash,
        'stage': stage,
        'message': message,
        "results":evaluate_results,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    progress_table.upsert(record, Query().request_id == request_id)

    print(f"{stage}: {message}")


def evaluate_model(request_id, source_file_hash, model_path, df, target_column):
    """
        对训练好的模型进行评估，并将结果保存到TinyDB。
        使用处理清理过的数据集(按训测试集比例划分)
        参数:
            - request_id: 请求 ID
            - source_file_hash: 数据源文件的hash值
            - model_path: 训练好的模型路径
            - df: 评估用的测试集数据
            - target_column: 目标列名
        返回:
            - evaluation_results: 评估结果
    """
    # 从 TinyDB 记录开始评估的时间
    log_progress(request_id, source_file_hash, "Model Evaluation", "Evaluation started")

    # 加载模型
    model = joblib.load(model_path)
    model_name = model.__class__.__name__

    # 特征工程
    df = train_model.feature_engineering(df, target_column)

    # 处理目标列编码（如果目标列是分类类型）
    le = LabelEncoder()
    if df[target_column].dtype == 'object':
        df[target_column] = le.fit_transform(df[target_column])

    # 对特征列进行编码（与训练时一致）
    for col in df.select_dtypes(include=['object']).columns:
        if col != target_column:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])

    # 划分特征和标签
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # 划分测试集
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 进行预测
    y_pred = model.predict(X_test)

    # 根据模型类型评估性能
    evaluation_results = {}
    if model_name in ['LinearRegression', 'RandomForestRegressor', 'DecisionTreeRegressor']:
        # 回归任务
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        evaluation_results['MSE'] = mse
        evaluation_results['RMSE'] = rmse
        print(f"MSE: {mse:.4f}")
        print(f"RMSE: {rmse:.4f}")
    else:
        # 分类任务
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        evaluation_results['Accuracy'] = accuracy
        evaluation_results['Precision'] = precision
        evaluation_results['Recall'] = recall
        evaluation_results['F1-Score'] = f1
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")

    # 保存评估结果到 TinyDB
    log_progress(request_id, source_file_hash, "Model Evaluation", "Evaluation completed", evaluation_results)

    return evaluation_results

