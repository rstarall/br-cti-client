import uuid
from ml.precess_data import read_file_as_df,clean_data
from ml.train_model import train_and_save_model
from ml.evaluate_model import evaluate_model
from env.global_var import getMlOutputDirPath
from db.tiny_db import TinyDBUtil
from utils.file import get_file_sha256_hash
from tinydb import Query
from ml.model_status import save_model_record,train_progress_callback,log_progress
import time
import os

# 自动生成请求 ID
def generate_request_id(source_file_hash):
    return str(uuid.uuid4())

def start_model_process_task(request_id,source_file_hash,source_file_path,target_label_column,cti_id=None):
    """
        启动模型训练(测试)任务
        参数:
        - request_id: 请求ID
        - source_file_hash: 训练源文件的HASH
        - source_file_path: 训练源文件的路径
        - target_label_column: 目标列的列名(label)
        - cti_id: CTI的ID
    """
    if request_id is None:
        return None, "request_id不能为空"
    if source_file_hash is None:
        return None, "source_file_hash不能为空"
    if source_file_path is None:
        return None, "source_file_path不能为空"
    if target_label_column is None:
        return None, "target_label_column不能为空"
    output_dir_path = getMlOutputDirPath()+f"/{source_file_hash}"
    # 记录模型信息
    model_info = {}
    if cti_id is not None:
        model_info["cti_id"] = cti_id
    else:
        model_info["cti_id"] = ""
    # 1.清理数据
    log_progress(request_id, source_file_hash, "Data Cleaning", "Data cleaning started")
    raw_df, err_msg = read_file_as_df(source_file_path)
    if raw_df is None:
        return None, err_msg
    df,clean_file_path, err_msg = clean_data(raw_df, source_file_hash,output_folder=output_dir_path)
    if df is None:
        return None, err_msg
    log_progress(request_id, source_file_hash, "Data Cleaning", "Data cleaning completed")

    #2.训练并保存模型
    try:
        
        model_info,model_save_path  = train_and_save_model(request_id,source_file_hash,
                                                           df=df,
                                                           output_dir_path=output_dir_path,
                                                           target_column=target_label_column,
                                                           callback=train_progress_callback)
    except Exception as e:
        save_model_record(request_id,'train_failed',source_file_hash,model_info)
        return None, str(e)
    save_model_record(request_id,'train_success',source_file_hash,model_info)
    #3.获取模型hash
    model_hash = get_model_hash(model_save_path)
    model_info['model_hash'] = model_hash
    model_info['evaluation_results'] = None
    #4.评估模型
    try:
        log_progress(request_id, source_file_hash, "Model Evaluation", "Model evaluation started")
        evaluation_results = evaluate_model(request_id,source_file_hash,
                       model_path=model_save_path,
                       df=df,
                        target_column=target_label_column)
        model_info['evaluation_results'] = evaluation_results
        log_progress(request_id, source_file_hash, "Model Evaluation", "Model evaluation completed",evaluate_results=evaluation_results)
    except Exception as e:
        save_model_record(request_id,'evaluate_failed',source_file_hash,model_info)
        return None, str(e)
    save_model_record(request_id,'evaluate_success',source_file_hash,model_info)
    return model_info, None

def get_model_hash(model_save_path):
    """
        获取模型hash(SHA256)
        return:
            - model_hash: 模型hash
    """
    if not os.path.exists(model_save_path):
        return ""
    return get_file_sha256_hash(model_save_path)
