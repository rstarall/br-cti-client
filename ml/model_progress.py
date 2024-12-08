from tinydb import TinyDB, Query
from db.tiny_db import TinyDBUtil
import time

# 初始化 TinyDB 数据库
progress_table = TinyDBUtil().use_database('ml_train_progress').open_table('train_progress')

def save_train_progress(request_id, source_file_hash, info):
    """
    保存训练进度信息
    参数:
        - request_id: 请求ID
        - source_file_hash: 数据源文件hash
        - info: 训练进度信息
    """
    progress_table.upsert({
        'request_id': request_id,
        'source_file_hash': source_file_hash,
        'progress_info': info,
        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }, Query().request_id == request_id)

def get_train_progress_by_id(request_id):
    """
    根据请求ID获取训练进度
    参数:
        - request_id: 请求ID
    返回:
        - record: 进度记录
    """
    records = progress_table.search(Query().request_id == request_id)
    return records[0] if records else None

def get_train_progress_by_hash(source_file_hash):
    """
    根据源文件hash获取训练进度
    参数:
        - source_file_hash: 源文件hash
    返回:
        - records: 进度记录列表
    """
    records = progress_table.search(Query().source_file_hash == source_file_hash)
    return records

def train_progress_callback(request_id, source_file_hash, info):
    # 保存进度信息
    save_train_progress(request_id, source_file_hash, info)
    
    # 打印进度信息
    print(f"进度: {info['train_progress_info']['progress']:.2f}%")
    print(f"训练集得分: {info['train_progress_info']['train_score']:.4f}")
    print(f"测试集得分: {info['train_progress_info']['test_score']:.4f}")
    print(f"已用时间: {info['train_progress_info']['time_elapsed']:.2f}秒")
    if 'current_iter' in info['train_progress_info']:
        print(f"当前迭代: {info['train_progress_info']['current_iter']}/{info['train_progress_info']['total_iter']}")
    print("-------------------")

info_name_map = {
    'train_progress_info': '训练进度信息',
    'model_select_info': '模型选择信息',
    'progress': '进度',
    'current_iter': '当前迭代',
    'total_iter': '总迭代次数',
    'train_score': '训练集得分',
    'test_score': '测试集得分',
    'time_elapsed': '已用时间',
    'n_samples': '样本数量',
    'n_features': '特征数量', 
    'numeric_features': '数值特征数量',
    'categorical_features': '类别特征数量',
    'n_classes': '类别数量'
}