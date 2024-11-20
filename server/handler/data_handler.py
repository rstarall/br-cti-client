from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
import os
from env.global_var import getUploadFilePath
from utils.file import replace_file_name_with_hash,get_date_file_dir,check_file_by_hash
from datetime import datetime
from service.data_service import DataService
data_blue = Blueprint('data',__name__,url_prefix='/data') #创建一个蓝图
data_service = DataService()
@data_blue.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"code":400,'error': 'No file part',"data":None})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code":400,'error': 'No selected file',"data":None})

    if file and allowed_file(file.filename):
        upload_file_path = get_date_file_dir(getUploadFilePath())
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


@data_blue.route('/get_traffic_data_features', methods=['POST'])
def get_traffic_data_features():
    print(request.json)
    data = request.get_json()
    print(data)
    file_hash = data.get('file_hash')
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    features_name,error = data_service.get_traffic_data_features_name(file_hash)
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    else:
        return jsonify({"code":200,'msg': 'Get traffic data features name successfully', 'data': features_name})

@data_blue.route('/process_data_to_stix', methods=['POST'])
def process_data_to_stix():
    data = request.get_json()
    file_hash = data.get('file_hash')
    process_config = data
    print(process_config)
    if not process_config:
        return jsonify({"code":400,'error': 'process_config is required',"data":None})
    if file_hash == "":
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    # 检查必要的配置参数
    # required_fields = ['file_hash','process_id', 'stix_type', 'stix_traffic_features', 
    #                   'stix_iocs', 'stix_label', 'stix_compress']

    required_fields = ['file_hash'] #暂时不需要配置
    required_fields_type = {
        "file_hash":str,
        "stix_compress":int
    }
    for field in required_fields:
        if field not in process_config:
            return jsonify({"code":400,'error': f'{field} is required in process_config',"data":None})
    #类型转换
    for field in required_fields_type.keys():
        if field  in process_config:
            process_config[field] = required_fields_type[field](process_config[field])
            
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    features_name,error = data_service.get_traffic_data_features_name(file_hash)
    #记录处理的文件hash,并处理文件
    current_step,total_step = data_service.process_data_to_stix(file_hash,process_config)
    data = {
        "current_step":current_step,
        "total_step":total_step
    }
    #记录处理过程
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    return jsonify({"code":200,'msg': 'Process data to stix successfully', 'data': data})

#查询处理进度
@data_blue.route('/get_stix_process_progress', methods=['POST'])
def get_process_progress():
    data = request.get_json()
    file_hash = data.get('file_hash')
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    progress = data_service.get_stix_process_progress(file_hash)
    return jsonify({"code":200,'msg': 'Get stix process progress successfully', 'data': progress})





#其他工具函数
def allowed_file(filename):
    return True
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}



