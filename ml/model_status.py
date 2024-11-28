from tinydb import TinyDB, Query
from db.tiny_db import TinyDBUtil
import time

# 初始化 TinyDB 数据库
progress_table = TinyDBUtil().use_database('ml_process_progress').open_table('progress')
ml_records_table = TinyDBUtil().use_database('ml_records').open_table('ml_records')

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
