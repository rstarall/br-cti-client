
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from utils.request import POST
bc_blue = Blueprint('bc',__name__,url_prefix='/blockchain') #创建一个蓝图

@bc_blue.route("/query-info-summary",methods=['GET'])
def query_info_summary():
    """
        获取Fabric区块链状态信息
        需要使用Fabric python sdK或者jsonrpc接口
    """
    try:
        result = POST(url='http://the-blockchain-api.com/v1/bc/info/summary',
                      data=None)
        data = result.get('data')
        if data != None:
            return jsonify({'code':200,"msg":"success","data": data})
        return jsonify({'code':502,"msg":'no data'})
    except Exception as e:
        return jsonify({"code":500,"msg": str(e)})