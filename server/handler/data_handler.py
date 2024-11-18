from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
import os
from env.global_var import getUploadFilePath
from utils.file import replace_file_name_with_hash,get_date_file_dir,check_file_by_hash
from datetime import datetime
data_blue = Blueprint('data',__name__,url_prefix='/data') #创建一个蓝图

@data_blue.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"code":400,'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"code":400,'error': 'No selected file'})

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
        return jsonify({"code":200,'msg': 'File uploaded successfully', 'data': data}), 200
    else:
        return jsonify({"code":400,'error': 'Invalid file type'})

#其他工具函数
def allowed_file(filename):
    return True
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}



