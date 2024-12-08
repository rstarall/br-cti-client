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
    
@ml_blue.route('/download_dataset_from_ipfs', methods=['POST'])
def download_dataset_from_ipfs():
    """
    从IPFS下载数据集文件
    """
    try:
        data = request.get_json()
        data_source_hash = data.get('data_source_hash')
        ipfs_hash = data.get('ipfs_hash')
        
        if not data_source_hash:
            return jsonify({'code': 400, 'msg': 'data_source_hash parameter is required'})
        if not ipfs_hash:
            return jsonify({'code': 400, 'msg': 'ipfs_hash parameter is required'})
            
        # 调用服务层方法下载文件
        file_info, error = ml_service.download_file_from_ipfs_by_hash(data_source_hash, ipfs_hash)
        if error:
            return jsonify({
                'code': 500,
                'msg': error,
                'error': '下载文件失败'
            })
               
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'file_info': file_info,
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': str(e),
            'error': '服务器内部错误'
        })

@ml_blue.route('/get_download_progress', methods=['POST']) 
def get_download_progress():
    """
    获取文件下载进度
    """
    try:
        data = request.get_json()
        data_source_hash = data.get('data_source_hash')
        
        if not data_source_hash:
            return jsonify({'code': 400, 'msg': 'data_source_hash parameter is required'})
            
        progress = ml_service.get_download_progress(data_source_hash)
        
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'progress': progress if progress else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500, 
            'msg': str(e),
            'error': '服务器内部错误'
        })

@ml_blue.route('/create_model_task', methods=['POST'])
def create_model_task():
    data = request.get_json()
    source_file_hash = data.get('file_hash',None)
    label_column = data.get('label_column',None)
    cti_id = data.get('cti_id',None)
    if not source_file_hash or not label_column:
        return jsonify({"code":400,'error': 'file_hash and label_column are required',"data":None})
    
    request_id,result = ml_service.createModelTask(source_file_hash, label_column,cti_id)
    if not result:
        return jsonify({"code":400,'error': 'Source file not found or invalid',"data":None})
        
    return jsonify({
        "code":200,
        'msg': 'Model task created successfully', 
        'data': {
            'request_id': request_id,
            'current_step': 1,
            'total_step': 4
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

@ml_blue.route('/get_train_progress_detail_by_id', methods=['POST'])
def get_train_progress_detail_by_id():
    data = request.get_json()
    request_id = data.get('request_id')
    
    if not request_id:
        return jsonify({"code":400,'error': 'request_id is required',"data":None})
    
    progress = ml_service.getTrainProgressDetailById(request_id)
    if not progress:
        return jsonify({"code":400,'error': 'Train progress detail not found',"data":None})
    return jsonify({"code":200,'msg': 'Get train progress detail successfully', 'data': progress})



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
    
    records = ml_service.getModelRecordsBySourceFileHash(file_hash)
    if not records:
        return jsonify({"code":400,'error': 'No model records found for this file',"data":None})
    return jsonify({"code":200,'msg': 'Get model records successfully', 'data': records})

@ml_blue.route('/get_feature_list', methods=['POST'])
def get_feature_list():
    data = request.get_json()
    file_hash = data.get('file_hash')
    
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    features_name,error = ml_service.get_feature_list(file_hash)
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    return jsonify({"code":200,'msg': 'Get  feature list successfully', 'data': features_name})


#根据源文件hash创建模型上链信息文件
@ml_blue.route('/create_model_upchain_info_by_source_file_hash', methods=['POST'])
def create_model_upchain_info_by_source_file_hash():
    data = request.get_json()
    file_hash = data.get('file_hash')
    model_info_config = data.get('model_info_config')
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    result = ml_service.createModelUpchainInfoBySourceFileHash(file_hash,model_info_config)
    if not result:
        return jsonify({"code":400,'error': '创建模型上链信息文件失败',"data":None})
    return jsonify({"code":200,'msg': '创建模型上链信息文件成功', 'data': None})

#创建模型上链信息文件
@ml_blue.route('/create_model_upchain_info', methods=['POST'])
def create_model_upchain_info():
    data = request.get_json()
    file_hash = data.get('file_hash')
    model_hash = data.get('model_hash')
    model_info_config = data.get('model_info_config')
    if not file_hash or not model_hash:
        return jsonify({"code":400,'error': 'file_hash and model_hash are required',"data":None})
    
    result = ml_service.createModelUpchainInfoFileSingle(file_hash,model_hash,model_info_config)
    if not result:
        return jsonify({"code":400,'error': 'Failed to create model upchain info file',"data":None})
    return jsonify({"code":200,'msg': 'Create model upchain info file successfully', 'data': None})
