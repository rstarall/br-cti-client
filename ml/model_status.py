from tinydb import TinyDB, Query
from db.tiny_db import TinyDBUtil
import time

example_model_record = {
    "request_id": "550e8400-e29b-41d4-a716-446655440000", # 请求ID
    "source_file_hash": "d41d8cd98f00b204e9800998ecf8427e", # 数据源文件hash
    "output_dir_path": "/path/to/output", # 输出目录路径
    "target_column": "label", # 目标列名
    "model_name": "RandomForestClassifier", # 模型名称
    "test_size": 0.2, # 测试集比例
    "model_save_path": "/path/to/model.joblib", # 模型保存路径
    "model_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", # 模型文件hash
    "pca": [0.5, 0.3, 0.1], # PCA主成分信息
    "training_time": 120.5, # 训练耗时(秒)
    "created_time": "2023-12-25 10:30:00", # 创建时间
    "evaluation_results": { # 评估结果
        "Accuracy": 0.95,
        "Precision": 0.94,
        "Recall": 0.93,
        "F1-Score": 0.94
    },
    "model_data_type": 1, #模型数据类型(1:流量(数据集)、2:情报(文本))
    "model_type": 1, #模型类型(1:分类模型、2:回归模型、3:聚类模型、4:NLP模型)
    "model_algorithm": "RandomForest", #模型算法
    "model_framework": "scikit-learn", #训练框架
    "features": [], #特征列表
    "model_size": 0, #模型大小(B)
    "data_size": 0, # 数据大小(B)
    "cti_id": "" # 关联的情报ID
}

# 初始化 TinyDB 数据库
progress_table = TinyDBUtil().use_database('ml_process_progress').open_table('progress')
ml_records_table = TinyDBUtil().use_database('ml_records').open_table('ml_records')
train_progress_table = TinyDBUtil().use_database('ml_records').open_table('train_progress')
# 定义处理步骤
PROCESS_STEPS = [
    "Data Cleaning",  # 数据清洗
    "Feature Engineering", # 特征工程
    "Label Encoding", # 标签编码
    "Train/Test Split", # 训练测试集划分
    "Model Training", # 模型训练
    "Model Saving", # 模型保存
    "Model Evaluation" # 模型评估
]
def save_model_record(request_id,status,source_file_hash,model_info:dict):
    """
        保存模型记录
        param:
            - request_id: 请求ID
            - source_file_hash: 数据源文件的hash值
            - status: 状态(训练完成，训练失败，评估完成，评估失败)
            - model_info: 模型信息
    """
    ml_records_table.upsert({
        'request_id': request_id,
        'source_file_hash': source_file_hash,
        'model_hash': model_info.get("model_hash",""),
        'onchain': False,
        'status': status,
        'model_info': model_info,
        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }, Query().request_id == request_id)

    print(f"request_id:{request_id}的模型记录已保存至 {ml_records_table}")

# 记录训练进度和评估信息
def log_progress(request_id, source_file_hash, stage, message, evaluate_results={}):
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
    # 获取当前步骤索引
    current_step = PROCESS_STEPS.index(stage) + 1 if stage in PROCESS_STEPS else 0
    total_steps = len(PROCESS_STEPS)

    record = {
        'request_id': request_id,
        'source_file_hash': source_file_hash,
        'stage': stage,
        'message': message,
        'results': evaluate_results,
        'current_step': current_step,
        'total_steps': total_steps,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    progress_table.upsert(record, Query().request_id == request_id)

    print(f"{stage} ({current_step}/{total_steps}): {message}")


def train_progress_callback(request_id, source_file_hash,info):
    print(f"进度: {info['train_progress_info']['progress']:.2f}%")
    print(f"训练集得分: {info['train_progress_info']['train_score']:.4f}")
    print(f"测试集得分: {info['train_progress_info']['test_score']:.4f}")
    print(f"已用时间: {info['train_progress_info']['time_elapsed']:.2f}秒")
    if 'current_iter' in info['train_progress_info']:
        print(f"当前迭代: {info['train_progress_info']['current_iter']}/{info['train_progress_info']['total_iter']}")
    print("-------------------")

def get_model_progress_status_by_id(request_id):
    """
        根据请求 ID 获取训练或测试的状态。

        参数:
        - request_id: 请求 ID
        返回:
        - record: 记录
    """
    records = progress_table.search(Query().request_id == request_id)
    return records[0]

def get_model_progress_status_by_hash(source_file_hash):
    """
        根据训练源文件的HASH获取训练或测试的状态。
        参数:
        - source_file_hash: 训练源文件的HASH
        返回:
        - records: 记录列表
    """
    records = progress_table.search(Query().source_file_hash == source_file_hash)
    return records

def get_model_record_by_id(request_id):
    """
        根据请求 ID 获取模型记录。
        参数:
        - request_id: 请求 ID

        返回:
        - record: 记录
    """
    records = ml_records_table.search(Query().request_id == request_id)
    return records[0]

def get_model_record_by_hash(source_file_hash):
    """
        根据训练源文件的HASH获取模型记录。
        参数:
        - source_file_hash: 训练源文件的HASH

        返回:
        - records: 记录列表
    """
    records = ml_records_table.search(Query().source_file_hash == source_file_hash)
    return records

def get_model_record_by_hash_and_hash(source_file_hash,model_hash):
    """
        根据源文件hash和模型hash获取模型记录
        param:
            - source_file_hash: 训练源文件的HASH
            - model_hash: 模型hash
        return:
            - record: 记录
    """
    records = ml_records_table.search(Query().source_file_hash == source_file_hash and Query().model_hash == model_hash)
    return records[0]
