from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from service.bc_service import BlockchainService
from utils.request import request_post,request_get
from env.global_var import fabricServerHost
index_blue = Blueprint('index',__name__,url_prefix='/') #创建一个蓝图
@index_blue.route("/",methods=['GET'])
def check_client_status():
    """
        检测client状态
    """
    return jsonify({"code":200,"msg": "success","data":""})