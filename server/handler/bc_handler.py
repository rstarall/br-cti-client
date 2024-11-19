
import json
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from service.bc_service import BlockchainService
from utils.request import request_post,request_get
from env.global_var import fabricServerHost
from utils.base64 import base64_to_binary
bc_blue = Blueprint('bc',__name__,url_prefix='/blockchain') #创建一个蓝图
bcService = BlockchainService()

@bc_blue.route("/query-network-info",methods=['GET'])
def query_network_status():
    """
        查询区块链网络信息
    """
    try:
        raw_data,ok = bcService.checkBlockchainStatus()
        data_str = raw_data["data"]
        data = json.loads(data_str)
        blockchainInfo={
            "height":data['BCI']["height"],
            "currentBlockHash": base64_to_binary(data['BCI']["currentBlockHash"]).hex(),
            "previousBlockHash":base64_to_binary(data['BCI']["previousBlockHash"]).hex(),
            "endorser":data["Endorser"],
        }
        if ok :
            return jsonify({'code':200,"msg":"success","data": blockchainInfo})
        return jsonify({'code':502,"msg":'blockchain network error'})
    except Exception as e:
        return jsonify({"code":500,"msg": str(e)})
    
@bc_blue.route("/query-block", methods=['GET'])
def query_block_height():
    """
        根据区块高度查询区块信息
    """
    try:
        # 从请求中获取 height 参数
        height = request.args.get('height', type=int)
        if height is None:
            return jsonify({'code': 400, 'msg': 'height parameter is required'})
        
        # 调用服务层方法查询区块信息
        block_info, ok = bcService.getBlockByHeight(height)
        if not ok:
            return jsonify({'code': 502, 'msg': 'blockchain network error','data':block_info})
        
        return jsonify({'code': 200, 'msg': 'success', 'data': block_info})
    
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})