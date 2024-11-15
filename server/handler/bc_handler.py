
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from service.bc_service import BlockchainService
from utils.request import request_post,request_get
from env.global_var import fabricServerHost
bc_blue = Blueprint('bc',__name__,url_prefix='/blockchain') #创建一个蓝图
bcService = BlockchainService()
@bc_blue.route("/query-info-summary",methods=['GET'])
def query_info_summary():
    """
        获取Fabric区块链状态信息
        需要使用Fabric python sdK或者jsonrpc接口
    """
    try:
        result = request_get(fabricServerHost+"/queryChain")
        data = result.get('data')
        if data != None:
            return jsonify({'code':200,"msg":"success","data": data})
        return jsonify({'code':502,"msg":'no data'})
    except Exception as e:
        return jsonify({"code":500,"msg": str(e)})

@bc_blue.route("/check-blockchain-status",methods=['GET'])
def check_blockchain_status():
    """
        检测区块链服务是否正常
    """
    try:
        data,ok = bcService.checkBlockchainStatus()
        if ok :
            return jsonify({'code':200,"msg":"success","data": data})
        return jsonify({'code':502,"msg":'blockchain error'})
    except Exception as e:
        return jsonify({"code":500,"msg": str(e)})