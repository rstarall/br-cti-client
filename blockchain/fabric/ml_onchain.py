import requests
from blockchain.fabric import env_vars
from blockchain.fabric.tx import createSignTransaction,createTransaction
import logging
import base64
import time
import json
def createModelUploadTransaction(wallet_id:str, password:str, model_data:dict)->dict:
    """
        创建模型上传链签名交易
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            model_data: 模型数据
        return:
            tx_msg: 交易消息
    """
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, model_data)
    
    # 将交易数据转换为bytes，使用base64编码
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"], 
        "nonce": tx_msg["nonce"],
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data


def createModelPurchaseTransaction(wallet_id:str, password:str, model_id:str)->dict:
    """
        创建模型购买链签名交易
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            model_id: 模型ID
        return:
            tx_msg: 交易消息
    """
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, {"model_id": model_id,"user_id":wallet_id})
    
    # 将交易数据转换为bytes，使用base64编码
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"], 
        "nonce": tx_msg["nonce"],
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data

def uploadModelToBlockchain(wallet_id:str, password:str, model_data:dict)->tuple[str,bool]:
    """
    执行智能合约上传模型数据到区块链
    params:
        wallet_id: 钱包ID
        password: 钱包密码
        model_data: 模型数据
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 创建交易消息
        tx_msg = createTransaction(wallet_id, password, model_data)
        
        tx_msg_data = {
            "user_id": str(tx_msg["user_id"]),
            "tx_data": tx_msg["tx_data"], 
            "nonce": tx_msg["nonce"],
            "tx_signature": tx_msg["tx_signature"],
            "nonce_signature": tx_msg["nonce_signature"]
        }
        print(tx_msg_data)
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['model']['registerModelInfo'],
                               json=tx_msg_data)
        logging.info("uploadModelToBlockchain response:"+str(response.json()))
        if response.status_code != 200:
            return response.json()['error'], False
        model_data = json.loads(response.json()['result'])    
        return model_data, True
        
    except Exception as e:
        return str(e), False

def purchaseModelFromBlockchain(wallet_id:str, password:str, model_id:str)->tuple[str,bool]:
    """
        购买模型
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            model_id: 模型ID
        return:
            (str,bool): (结果信息,是否成功)
    """
    try:
        # 创建交易消息
        tx_msg = createModelPurchaseTransaction(wallet_id, password, model_id)
        
        # 构造请求数据
        tx_msg_data = {
            "user_id": str(tx_msg["user_id"]),
            "tx_data": tx_msg["tx_data"],
            "nonce": tx_msg["nonce"],
            "tx_signature": tx_msg["tx_signature"], 
            "nonce_signature": tx_msg["nonce_signature"]
        }

        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['purchaseModel'],
                               json=tx_msg_data)
        logging.info("purchaseModelFromBlockchain response:"+str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False
