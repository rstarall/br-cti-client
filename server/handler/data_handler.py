from flask import Flask,jsonify,request,Response
import logging
from flask import Blueprint  # 导入蓝图模块
import os
from env.global_var import getUploadFilePath
from utils.file import replace_file_name_with_hash,get_date_file_dir,check_file_by_hash
from datetime import datetime
from service.data_service import DataService
import json
import random


data_blue = Blueprint('data',__name__,url_prefix='/data')  # 创建一个蓝图
data_service = DataService()


# 其他工具函数
def allowed_file(filename):
    return True
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx','json','jsonl','txt'}


# 上传本地数据集文件
@data_blue.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"code":400,'error': 'No file part',"data":None})

    file = request.files['file']
    task_id = request.form.get('task_id',"")
    if task_id == "":
        return jsonify({"code":400,'error': 'task_id is required',"data":None})
    if file.filename == '':
        return jsonify({"code":400,'error': 'No selected file',"data":None})

    if file and allowed_file(file.filename):
        upload_file_path = get_date_file_dir(getUploadFilePath())
        temp_filename = os.path.join(upload_file_path, file.filename)
        file.save(temp_filename)
        # 将文件名替换为文件的sha256哈希值
        file_hash,file_size = replace_file_name_with_hash(temp_filename)
        # 查询是否有当前文件的任务记录
        latest_task_record = data_service.get_latest_task_record(file_hash)
        if latest_task_record is None:
            latest_task_record = data_service.create_task_record(task_id,file_hash)  # 创建任务记录
        
        data = {
            "file_hash":file_hash,
            "file_size":file_size,
            "task_record":latest_task_record
        }
        return jsonify({"code":200,'msg': 'File uploaded successfully', 'data': data})
    else:
        return jsonify({"code":400,'error': 'Invalid file type',"data":None})


# 查询文件特征字段
@data_blue.route('/get_traffic_data_features', methods=['POST'])
def get_traffic_data_features():
    print(request.json)
    data = request.get_json()
    print(data)
    file_hash = data.get('file_hash')
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    features_name,error = data_service.get_feature_list(file_hash)
    if error:
        return jsonify({"code":400,'error': error,"data":None})
    else:
        return jsonify({"code":200,'msg': 'Get traffic data features name successfully', 'data': features_name})


# 将数据集文件转换成STIX格式文件
@data_blue.route('/process_data_to_stix', methods=['POST'])
def process_data_to_stix():
    data = request.get_json()
    task_id = data.get('process_id',"")  # 记录任务ID
    file_hash = data.get('file_hash',"")
    stix_process_config = data
    if not stix_process_config:
        return jsonify({"code":400,'error': 'stix_process_config is required',"data":None})
    if file_hash == "":
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    # 检查必要的配置参数
    # required_fields = ['file_hash','process_id', 'stix_type', 'stix_traffic_features', 
    #                   'stix_iocs', 'stix_label', 'stix_compress']

    required_fields = ['file_hash']  # 暂时不需要配置
    required_fields_type = {
        "file_hash":str,
        "stix_compress":int
    }
    for field in required_fields:
        if field not in stix_process_config:
            return jsonify({"code":400,'error': f'{field} is required in process_config',"data":None})
    # 类型转换
    for field in required_fields_type.keys():
        if field  in stix_process_config:
            stix_process_config[field] = required_fields_type[field](stix_process_config[field])

    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    # 记录处理的文件hash,并处理文件
    try:
        current_step,total_step = data_service.process_data_to_stix(file_hash,stix_process_config)
    except Exception as e:
        return jsonify({"code":400,'error': str(e),"data":None})
    data = {
        "current_step":current_step,
        "total_step":total_step
    }
    return jsonify({"code":200,'msg': 'Process data to stix successfully', 'data': data})


# 查询处理进度
@data_blue.route('/get_stix_process_progress', methods=['POST'])
def get_process_progress():
    data = request.get_json()
    file_hash = data.get('file_hash')
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    progress = data_service.get_stix_process_progress(file_hash)

    # 加上有效性判断
    if progress:
        return jsonify({"code":200,'msg': 'Get stix process progress successfully', 'data': progress})
    else:
        return jsonify({"code": 400, 'error': '无该文件对应的处理进度！若文件已处理完成，请查找stix记录！', "data": None})


# 查询stix记录表,支持分页
@data_blue.route('/get_local_stix_records', methods=['GET','POST'])
def get_local_stix_records():
    data = {}
    if request.method == 'GET':
        data = request.args
    else:
        data = request.get_json()
    file_hash = data.get('file_hash',None)
    page = data.get('page',None)
    page_size = data.get('page_size',None)
    if not file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    if not page or not page_size:
        all = True
    else:
        all = False
    records = data_service.get_local_stix_records(file_hash,page,page_size,all)
    if records:
        return jsonify({"code":200,'msg': 'Get stix records successfully', 'data': records})
    else:
        return jsonify({"code":400,'error': 'No stix records found',"data":None})


# 查询stix文件内容
@data_blue.route('/get_stix_file_content/<source_file_hash>/<stix_file_hash>', methods=['GET'])
def get_stix_file_content(source_file_hash, stix_file_hash):
    if source_file_hash == "" or stix_file_hash == "":
        return jsonify({"code":400,'error': 'stix_file_hash or source_file_hash is required',"data":None})
    stix_data = data_service.get_local_stix_file_by_hash(source_file_hash,stix_file_hash)
    if stix_data is not None:
        # 直接返回json文本
        return Response(stix_data, content_type='application/json')
    else:
        return jsonify({"code":400,'error': 'No stix file found',"data":None})


# 处理本地STIX数据，生成本地上链情报
@data_blue.route('/process_stix_to_cti', methods=['POST'])
def process_stix_to_cti():
    data = request.get_json()
    source_file_hash = data.get('file_hash',None)
    cti_type = data.get('cti_type',1)
    cti_default_name = data.get('cti_name',"")
    open_source = data.get('open_source',1)
    cti_description = data.get('cti_description',"")
    default_value = data.get('default_value',10)
    print(f"process_stix_to_cti config:{data}")
    if not source_file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    
    # 判断类型正确性
    if type(cti_type) != int:
        cti_type = 1  # 默认设置为恶意流量
    if type(open_source) != int:
        open_source = 1  # 默认设置为开源情报
    if type(default_value) != int:
        default_value = 10  # 默认设置为10
    if type(cti_description) != str:
        cti_description = ""  # 默认设置为空
    cti_config = {
        "cti_type": cti_type,
        "cti_traffic_type": random.randint(1,3),  # 随机生成一个流量类型(1:5G,2:卫星网络,3:SDN)
        "cti_name": cti_default_name,
        "open_source": open_source,
        "description": cti_description,
        "value": default_value
    }
    data_service.start_create_local_cti_records_by_hash(source_file_hash, cti_config)
    
    # 获取当前处理进度
    data_service.get_cti_process_progress(source_file_hash)
    return jsonify({
        "code":200,
        'msg': 'start create local cti records by hash', 
        'data': {
            "current_step": 0,
            "total_step": 0
        }
    })


# 查询情报处理进度
@data_blue.route('/get_cti_process_progress', methods=['POST'])
def get_cti_process_progress():
    data = request.get_json()
    source_file_hash = data.get('file_hash',None)
    if not source_file_hash:
        return jsonify({"code":400,'error': 'file_hash is required',"data":None})
    progress = data_service.get_cti_process_progress(source_file_hash)
    return jsonify({"code":200,'msg': 'Get cti process progress successfully', 'data': progress})
