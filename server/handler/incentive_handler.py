from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from blockchain.fabric import incentive

incentive_blue = Blueprint('incentive',__name__,url_prefix='/incentive') #创建一个蓝图

#注册文档激励信息
@incentive_blue.route('/registerDocIncentiveInfo',methods=['POST'])
def registerDocIncentiveInfo():
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    incentive_data = request.json.get('incentive_data')
    if not wallet_id or not password or not incentive_data:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result,success = incentive.registerDocIncentiveInfo(wallet_id, password, incentive_data)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#查询文档激励信息
@incentive_blue.route('/queryDocIncentiveInfo',methods=['POST'])
def queryDocIncentiveInfo():
    ref_id = request.json.get('ref_id')
    doc_type = request.json.get('doc_type')
    if not ref_id or not doc_type:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result,success = incentive.queryDocIncentiveInfo(ref_id, doc_type)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#创建激励交易
@incentive_blue.route('/createIncentiveTransaction',methods=['POST'])
def createIncentiveTransaction():
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    incentive_data = request.json.get('incentive_data')
    if not wallet_id or not password or not incentive_data:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result = incentive.createIncentiveTransaction(wallet_id, password, incentive_data)
    if result:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})
