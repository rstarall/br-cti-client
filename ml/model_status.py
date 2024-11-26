from tinydb import TinyDB, Query
from db.tiny_db import TinyDBUtil
# 初始化 TinyDB 数据库
progress_table = TinyDBUtil().use_database('ml_process_progress').open_table('progress')
ml_records_table = TinyDBUtil().use_database('ml_records').open_table('ml_records')

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
