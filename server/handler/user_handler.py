
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from service.wallet_service import WalletService
user_blue = Blueprint('user',__name__,url_prefix='/user') #创建一个蓝图

wallet_service = WalletService()

#检查本地钱包
@user_blue.route('/checkLocalUserWallet',methods=['GET','POST'])
def checkLocalUserWallet():
    wallet_id = wallet_service.checkUserAccountExist()
    print(wallet_id)
    if wallet_id is  None:
        return jsonify({'code': 400, 'message': 'account not exist', 'data': None})
    else:
        return jsonify({'code': 200, 'message': 'success', 'data': {'wallet_id': wallet_id}})

#检查本地钱包是否已上链
@user_blue.route('/checkLocalWalletOnchainStatus',methods=['POST'])
def checkLocalWalletOnchainStatus():
    wallet_id = request.json.get('wallet_id')
    if not wallet_id:
        return jsonify({'code': 400, 'message': 'wallet_id is required', 'data': None})
    result = wallet_service.checkLocalWalletOnchainStatus(wallet_id)
    return jsonify({'code': 200, 'message': 'success', 'data': {'onchain': result}})

#创建本地钱包
@user_blue.route('/createLocalUserWallet',methods=['POST'])
def createLocalUserWallet():
    password = request.json.get('password')
    if not password:
        return jsonify({'code': 400, 'message': 'password is required', 'data': None})
    result,success = wallet_service.createLocalUserWallet(password)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': {'wallet_id': result}})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#检查钱包密码
@user_blue.route('/checkWalletPassword',methods=['POST'])
def checkWalletPassword():
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    if not wallet_id or not password:
        return jsonify({'code': 400, 'message': 'wallet_id or password is required', 'data': None})
    result = wallet_service.checkWalletPassword(wallet_id, password)
    return jsonify({'code': 200, 'message': 'success', 'data': result})

#注册用户账户(链上注册)
@user_blue.route('/registerOnchainUserAccount',methods=['POST'])
def registerOnchainUserAccount():
    wallet_id = request.json.get('wallet_id')
    user_name = request.json.get('user_name','')
    if not wallet_id:
        return jsonify({'code': 400, 'message': 'wallet_id is required', 'data': None})
    #注册钱包链上信息
    result,success = wallet_service.registerOnchainUserAccount(wallet_id,user_name)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': {'wallet_id': result}})
    else:
        #链上注册失败直接返回钱包ID
        return jsonify({'code': 200, 'message': result, 'data': {'wallet_id': result}})


#查询用户积分信息
@user_blue.route('/queryUserPointInfo',methods=['POST'])
def queryUserPointInfo():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id is required', 'data': None})
    result,success = wallet_service.queryUserPointInfo(user_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})


#获取用户统计数据
@user_blue.route('/getUserStatistics',methods=['POST'])
def getUserStatistics():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id is required', 'data': None})
    result,success = wallet_service.getUserStatistics(user_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#查询用户积分交易记录
@user_blue.route('/queryPointTransactions',methods=['POST']) 
def queryPointTransactions():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id is required', 'data': None})
    result,success = wallet_service.queryPointTransactions(user_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})


#获取交易随机数
@user_blue.route('/getTransactionNonce',methods=['POST'])
def getTransactionNonce():
    wallet_id = request.json.get('wallet_id')
    tx_sign = request.json.get('tx_sign')
    result,success = wallet_service.getSignatureNonce(wallet_id,tx_sign)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': {'nonce': result}})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})