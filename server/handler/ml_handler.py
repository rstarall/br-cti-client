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
    if label_column == "empty_label":
        label_column = ""
    request_id,result = ml_service.createModelTask(source_file_hash, label_column,cti_id)
    if not result:
        return jsonify({"code":400,'error': 'Source file not found or invalid',"data":None})
    
    return jsonify({
        "code":200,
        'msg': 'Model task created successfully', 
        'data': {
            'request_id': request_id,
            'current_step':  1,
            'total_step':  7
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

@ml_blue.route('/get_train_process_image', methods=['POST'])
def get_train_process_image():
    """
    获取训练过程图像
    """
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({
                "code": 400,
                'error': '请求ID不能为空',
                "data": None
            })
        
        # 获取base64格式的图像数据
        image_base64 = ml_service.get_train_process_image_base64(request_id)
        if not image_base64:
            return jsonify({
                "code": 400,
                'error': '获取训练过程图像失败',
                "data": None
            })
            
        return jsonify({
            "code": 200,
            'msg': '获取训练过程图像成功', 
            'data': {
                'image_base64': image_base64,
                'image_type': 'png'
            }
        })
    except Exception as e:
        logging.error(f"获取训练过程图像失败: {str(e)}")
        return jsonify({
            "code": 500,
            'error': f'服务器内部错误: {str(e)}',
            "data": None
        })

@ml_blue.route('/get_model_evaluate_image', methods=['POST']) 
def get_model_evaluate_image():
    """
    获取模型评估图像
    """
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({
                "code": 400,
                'error': '请求ID不能为空',
                "data": None
            })
        
        # 获取base64格式的图像数据
        image_base64 = ml_service.get_model_evaluate_image_base64(request_id)
        if not image_base64:
            return jsonify({
                "code": 400,
                'error': '获取模型评估图像失败',
                "data": None
            })
            
        return jsonify({
            "code": 200,
            'msg': '获取模型评估图像成功', 
            'data': {
                'image_base64': image_base64,
                'image_type': 'png'
            }
        })
    except Exception as e:
        logging.error(f"获取模型评估图像失败: {str(e)}")
        return jsonify({
            "code": 500,
            'error': f'服务器内部错误: {str(e)}',
            "data": None
        })



@ml_blue.route('/get_model_record_by_request_id', methods=['POST'])
def get_model_record_by_request_id():
    data = request.get_json()
    request_id = data.get('request_id')
    
    if not request_id:
        return jsonify({"code":400,'error': 'request_id is required',"data":None})
    
    record = ml_service.getModelRecordByRequestId(request_id)
    if not record:
        return jsonify({"code":400,'error': 'Model record not found',"data":None})
    return jsonify({"code":200,'msg': 'Get model record successfully', 'data': record})

@ml_blue.route('/get_model_record_list_by_hash', methods=['POST'])
def get_model_record_list_by_hash():
    """
        根据源文件hash获取模型训练记录列表
    """
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
    #入参类型进行判断
    if not isinstance(model_info_config, dict):
        return jsonify({"code":400,'error': 'model_info_config must be a dictionary',"data":None})
    
    if not isinstance(model_info_config.get("tags",[]), list):
        model_info_config["model_tags"] = list(model_info_config.get("tags",[]))
    if not isinstance(model_info_config.get("value",0), int):
        model_info_config["value"] = int(model_info_config.get("value",0))
        
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
    #入参类型进行判断
    if not isinstance(model_info_config, dict):
        return jsonify({"code":400,'error': 'model_info_config must be a dictionary',"data":None})
    
    if not isinstance(model_info_config.get("tags",[]), list):
        model_info_config["model_tags"] = list(model_info_config.get("tags",[]))
    value = model_info_config.get("value", 0)
    model_info_config["value"] = int(value) if value != '' else 0
        
    result,error = ml_service.createModelUpchainInfoFileSingle(file_hash,model_hash,model_info_config)
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    return jsonify({"code":200,'msg': 'Create model result info file successfully', 'data': result})
