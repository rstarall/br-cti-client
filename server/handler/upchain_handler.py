
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