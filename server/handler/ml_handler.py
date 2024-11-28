from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from utils.file import replace_file_name_with_hash,get_date_file_dir
from env.global_var import getMlOutputDirPath,getMlUploadFilePath
from service.ml_service import MLService
import os
ml_blue = Blueprint('ml',__name__,url_prefix='/ml') #创建一个蓝图
ml_service = MLService()
#其他工具函数
def allowed_file(filename):
    return True

@ml_blue.route('/upload_dataset_file', methods=['POST'])
def upload_dataset_file():
    if 'file' not in request.files:
        return jsonify({"code":400,'error': 'No file part',"data":None})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code":400,'error': 'No selected file',"data":None})

    if file and allowed_file(file.filename):
        upload_file_path = get_date_file_dir(getMlUploadFilePath())
        temp_filename   = os.path.join(upload_file_path, file.filename)
        file.save(temp_filename)
        # 将文件名替换为文件的sha256哈希值
        file_hash,file_size = replace_file_name_with_hash(temp_filename)
        data = {
            "file_hash":file_hash,
            "file_size":file_size
        }
        return jsonify({"code":200,'msg': 'File uploaded successfully', 'data': data})
    else:
        return jsonify({"code":400,'error': 'Invalid file type',"data":None})
    

@ml_blue.route('/create_model_task', methods=['POST'])
def create_model_task():
    data = request.get_json()
    source_file_hash = data.get('file_hash',None)
    label_column = data.get('label_column',None)
    
    if not source_file_hash or not label_column:
        return jsonify({"code":400,'error': 'file_hash and label_column are required',"data":None})
    
    result = ml_service.createModelTask(source_file_hash, label_column)
    if not result:
        return jsonify({"code":400,'error': 'Source file not found or invalid',"data":None})
        
    # 返回当前进度信息
    progress = ml_service.getModelProgressByHash(source_file_hash)
    if not progress or len(progress) == 0:
        return jsonify({"code":400,'error': 'Failed to get model progress',"data":None})
        
    latest_progress = progress[-1]
    return jsonify({
        "code":200,
        'msg': 'Model task created successfully', 
        'data': {
            'current_step': latest_progress.get('current_step'),
            'total_step': latest_progress.get('total_steps'),
            'request_id': latest_progress.get('request_id')
        }
    })

@ml_blue.route('/get_model_progress', methods=['POST'])
def get_model_progress():
    data = request.get_json()
    request_id = data.get('request_id')
    
    if not request_id:
        return jsonify({"code":400,'error': 'request_id is required',"data":None})
    
    progress = ml_service.getModelProgress(request_id)
    if not progress:
        return jsonify({"code":400,'error': 'Model progress not found',"data":None})
    return jsonify({"code":200,'msg': 'Get model progress successfully', 'data': progress})

@ml_blue.route('/get_model_progress_by_hash', methods=['POST'])
def get_model_progress_by_hash():
    data = request.get_json()
    file_hash = data.get('file_hash')
    
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    progress_list = ml_service.getModelProgressByHash(file_hash)
    if not progress_list or len(progress_list) == 0:
        return jsonify({"code":400,'error': 'Failed to get model progress',"data":None})
        
    progress = progress_list[-1]
    if not progress:
        return jsonify({"code":400,'error': 'No model progress found for this file',"data":None})
    return jsonify({"code":200,'msg': 'Get model progress list successfully', 'data': progress})

@ml_blue.route('/get_model_record', methods=['POST'])
def get_model_record():
    data = request.get_json()
    request_id = data.get('request_id')
    
    if not request_id:
        return jsonify({"code":400,'error': 'request_id is required',"data":None})
    
    record = ml_service.getModelRecord(request_id)
    if not record:
        return jsonify({"code":400,'error': 'Model record not found',"data":None})
    return jsonify({"code":200,'msg': 'Get model record successfully', 'data': record})

@ml_blue.route('/get_model_records_by_hash', methods=['POST'])
def get_model_records_by_hash():
    data = request.get_json()
    file_hash = data.get('file_hash')
    
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    records = ml_service.getModelRecordsByHash(file_hash)
    if not records:
        return jsonify({"code":400,'error': 'No model records found for this file',"data":None})
    return jsonify({"code":200,'msg': 'Get model records successfully', 'data': records})

@ml_blue.route('/get_traffic_feature_list', methods=['POST'])
def get_traffic_feature_list():
    data = request.get_json()
    file_hash = data.get('file_hash')
    
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    features_name,error = ml_service.get_traffic_feature_list(file_hash)
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    return jsonify({"code":200,'msg': 'Get traffic feature list successfully', 'data': features_name})

