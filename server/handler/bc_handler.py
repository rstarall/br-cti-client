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

#---------------------------------------------------CTI上链---------------------------------------------------
@bc_blue.route("/upload_cti", methods=['POST'])
def upload_cti_to_blockchain():
    """
        上传CTI数据到区块链
    """
    try:
        data = request.get_json()
        # 获取所有必需的参数
        source_file_hash = data.get('file_hash')
        ipfs_address = data.get('ipfs_address')
        upchain_account = data.get('upchain_account')
        upchain_account_password = data.get('upchain_account_password')
        
        # 验证必需的参数
        if not all([source_file_hash, ipfs_address, upchain_account, upchain_account_password]):
            return jsonify({
                'code': 400, 
                'msg': 'Missing required parameters',
                'error': '缺少必需的参数'
            })
        
        # 调用服务层方法上传CTI数据
        result, ok = bcService.uploadCTIToBCByFileSourceHash(source_file_hash,upchain_account,upchain_account_password)
        if not ok:
            if result == "no_cti_data":
                return jsonify({
                    'code': 400, 
                    'msg': 'no cti data',
                    'error': '没有未上链的CTI数据'
                })
            return jsonify({
                'code': 502, 
                'msg': result,
                'error': '区块链网络错误'
            })
        
        # 获取进度信息
        progress = bcService.getCTIUpchainProgress(source_file_hash)
             
        return jsonify({
            'code': 200, 
            'msg': 'success', 
            'data': {
                'current_step': progress.get('current_step',0),
                'total_step': progress.get('total_step',0),
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500, 
            'msg': str(e),
            'error': '服务器内部错误'
        })

@bc_blue.route("/get_upload_cti_progress", methods=['POST'])
def get_upload_cti_progress():
    """
        获取CTI数据上链进度
    """
    try:
        data = request.get_json()
        source_file_hash = data.get('file_hash')
        
        if not source_file_hash:
            return jsonify({'code': 400, 'msg': 'file_hash parameter is required'})
        
        # 获取上链进度
        progress = bcService.getCTIUpchainProgress(source_file_hash)
        return jsonify({'code': 200, 'msg': 'success', 'data': progress})
    
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})
    
#---------------------------------------------------模型上链---------------------------------------------------

@bc_blue.route("/upload_model_to_bc_by_source_file_hash", methods=['POST'])
def upload_model_to_bc_by_source_file_hash():
    """
        上传模型数据到区块链
    """
    try:
        data = request.get_json()
        source_file_hash = data.get('file_hash')
        upchain_account = data.get('upchain_account')
        upchain_account_password = data.get('upchain_account_password')
        
        if not source_file_hash:
            return jsonify({'code': 400, 'msg': 'file_hash parameter is required'})
        if not upchain_account:
            return jsonify({'code': 400, 'msg': 'upchain_account parameter is required'})
        if not upchain_account_password:
            return jsonify({'code': 400, 'msg': 'upchain_account_password parameter is required'})
        
        # 调用服务层方法上传模型数据
        result, ok = bcService.uploadModelToBCByFileSourceHash(source_file_hash,upchain_account,upchain_account_password)
        if not ok:
            return jsonify({
                'code': 502, 
                'msg': result,
                'error': '区块链网络错误'
            })
        
        # 获取进度信息
        progress = bcService.getModelUpchainProgress(source_file_hash)
             
        return jsonify({
            'code': 200, 
            'msg': 'success', 
            'data': {
                'current_step': progress.get('current_step',0),
                'total_step': progress.get('total_step',0),
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500, 
            'msg': str(e),
            'error': '服务器内部错误'
        })

@bc_blue.route("/upload_model_to_bc_by_model_hash", methods=['POST'])
def upload_model_to_bc_by_model_hash():
    """
        上传模型数据到区块链
    """
    try:
        data = request.get_json()
        source_file_hash = data.get('file_hash')
        model_hash = data.get('model_hash')
        upchain_account = data.get('upchain_account')
        upchain_account_password = data.get('upchain_account_password')
        
        if not source_file_hash:
            return jsonify({'code': 400, 'msg': 'file_hash parameter is required'})
        if not model_hash:
            return jsonify({'code': 400, 'msg': 'model_hash parameter is required'})
        if not upchain_account:
            return jsonify({'code': 400, 'msg': 'upchain_account parameter is required'})
        if not upchain_account_password:
            return jsonify({'code': 400, 'msg': 'upchain_account_password parameter is required'})
        
        # 调用服务层方法上传模型数据
        result, ok = bcService.uploadModelToBCByModelHash(source_file_hash, model_hash, upchain_account, upchain_account_password)
        if not ok:
            return jsonify({
                'code': 502,
                'msg': result, 
                'error': '区块链网络错误'
            })
            
        # 获取进度信息
        progress = bcService.getModelUpchainProgress(source_file_hash)
        
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'current_step': progress.get('current_step',0),
                'total_step': progress.get('total_step',0),
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': str(e),
            'error': '服务器内部错误'
        })

@bc_blue.route("/get_upload_model_progress", methods=['POST'])
def get_upload_model_progress():
    """
        获取模型数据上链进度
    """
    try:
        data = request.get_json()
        source_file_hash = data.get('file_hash')
        
        if not source_file_hash:
            return jsonify({'code': 400, 'msg': 'file_hash parameter is required'})
        
        # 获取上链进度
        progress = bcService.getModelUpchainProgress(source_file_hash)
        return jsonify({'code': 200, 'msg': 'success', 'data': progress})
    
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})
