
"""
    上链处理（情报、用户、资产）
"""
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from service.bc_service import BlockchainService

upchain_blue = Blueprint('upchain',__name__,url_prefix='/upchain') #创建一个蓝图
bc_service = BlockchainService()

#获取IPFS地址
@upchain_blue.route('/getIPFSAddress',methods=['POST',"GET"])
def getIPFSAddress():
    ipfs_address = bc_service.getIPFSAddress()
    if ipfs_address is None:
        return jsonify({'code': 400, 'message': 'failed', 'data': None})
    else:
        return jsonify({'code': 200, 'message': 'success', 'data': {'ipfs_address': ipfs_address}})
    
#创建CTI上传链签名交易
@upchain_blue.route('/create_cti_upload_transaction',methods=['POST'])
def create_cti_upload_transaction():
    """
        创建CTI上传链签名交易
    """
    try:
        data = request.get_json()
        # 获取所有必需的参数
        wallet_id = data.get('wallet_id')
        password = data.get('password')
        cti_data = {
            "cti_id": data.get("cti_id", ""),  # 情报ID(链上生成)
            "cti_hash": data.get("cti_hash", ""),  # 情报HASH(sha256链下生成) 
            "cti_name": data.get("cti_name", ""),  # 情报名称(可为空)
            "cti_type": data.get("cti_type", 0),  # 情报类型（1:恶意流量、2:蜜罐情报、3:僵尸网络、4:应用层攻击、5:开源情报）
            "cti_traffic_type": data.get("cti_traffic_type", 0),  # 流量情报类型（0:非流量、1:5G、2:卫星网络、3:SDN）
            "open_source": data.get("open_source", 0),  # 是否开源（0不开源，1开源）
            "creator_user_id": data.get("wallet_id", ""),  # 创建者ID
            "tags": data.get("tags", []),  # 情报标签数组
            "iocs": data.get("iocs", []),  # 包含的沦陷指标（IP, Port, Payload,URL, Hash）
            "stix_data": data.get("stix_data", ""),  # STIX数据（JSON）或者IPFS HASH
            "statistic_info": data.get("statistic_info", ""),  # 统计信息(JSON) 或者IPFS HASH
            "description": data.get("description", ""),  # 情报描述
            "data_size": data.get("data_size", 0),  # 数据大小（B）
            "data_hash": data.get("data_hash", ""),  # 情报STIX数据HASH（sha256）
            "ipfs_hash": data.get("ipfs_hash", ""),  # IPFS地址(STIX数据或者统计信息)
            "value": data.get("value", 0),  # 情报价值（积分）
        }
        # 验证必需的参数
        if not all([wallet_id, password, cti_data]):
            return jsonify({
                'code': 400, 
                'msg': 'Missing required parameters',
                'error': '缺少必需的参数'
            })
        
        # 调用服务层方法创建交易
        tx_msg = bc_service.createCTIUploadTransaction(wallet_id, password, cti_data)
        
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': tx_msg
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': str(e),
            'error': '服务器内部错误'
        })
