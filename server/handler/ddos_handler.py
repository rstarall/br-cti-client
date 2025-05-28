from flask import Flask, jsonify, request, Response
import logging
from flask import Blueprint  # 导入蓝图模块
import os
from env.global_var import getUploadFilePath
from utils.file import replace_file_name_with_hash, get_date_file_dir, check_file_by_hash
from datetime import datetime
from ability.ddos_ability.FlaskProject.ddos_ability import DdosAbility  # 西电后端服务接口
import json
import random


ddos_blue = Blueprint('ddos', __name__, url_prefix='/ddos')  # 创建一个蓝图
ddos_service = DdosAbility()


# DDos检测演示接口
@ddos_blue.route('/ddos_ability/<file>', methods=['GET'])
def ddos_ability(file):
    # 从路由参数直接获取文件名
    filename = file  # 使用路由参数中的文件名

    # 验证文件名有效性
    if not filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename', "data": None}), 400

    # 直接使用路由参数调用西电后端服务接口
    result, status = ddos_service.data(filename)
    if status == "fail":
        return result, 400  # 失败返回 400 状态码和错误信息
    elif status == "success":
        return result, 200  # 成功返回 200 状态码和时间线数据



