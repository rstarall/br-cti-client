import requests
from blockchain.fabric import env_vars
from blockchain.fabric.tx import createSignTransaction,createTransaction
import logging
import base64
import time
import json
def createCTIUploadTransaction(wallet_id:str, password:str, cti_data:dict)->dict:
    """
        创建CTI上传链签名交易
    """
    # 创建签名交易
    #tx_msg = createSignTransaction(wallet_id, password, cti_data)
    # 暂时不需要签名
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, cti_data)
    
    # 将交易数据转换为bytes，使用base64编码
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"], 
        "nonce": tx_msg["nonce"],
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data

def uploadCTIToBlockchain(wallet_id:str, password:str, cti_data:dict)->tuple[str,bool]:
    """
    执行智能合约上传CTI数据到区块链
    params:
        wallet_id: 钱包ID
        password: 钱包密码
        cti_data: CTI数据
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 创建签名交易
        #tx_msg = createSignTransaction(wallet_id, password, cti_data)
        # 暂时不需要签名
        # 创建交易消息
        tx_msg = createTransaction(wallet_id, password, cti_data)
        
        tx_msg_data = {
            "user_id": str(tx_msg["user_id"]),
            "tx_data": tx_msg["tx_data"], 
            "nonce": tx_msg["nonce"],
            "tx_signature": tx_msg["tx_signature"],
            "nonce_signature": tx_msg["nonce_signature"]
        }
        print(tx_msg_data)
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['cti']['registerCtiInfo'],
                               json=tx_msg_data)
        logging.info("uploadCTIToBlockchain response:"+str(response.json()))
        if response.status_code != 200:
            return response.json()['error'], False
        cti_data = json.loads(response.json()['result'])    
        return cti_data, True
        
    except Exception as e:
        return str(e), False


def createCTIPurchaseTransaction(wallet_id:str, password:str, cti_id:str)->dict:
    """
        创建CTI购买链签名交易
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            cti_id: CTI数据ID
        return:
            tx_msg: 交易消息
    """
    # 创建签名交易
    #tx_msg = createSignTransaction(wallet_id, password, cti_data)
    # 暂时不需要签名
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, {"cti_id": cti_id,"user_id":wallet_id})
    
    # 将交易数据转换为bytes，使用base64编码
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"], 
        "nonce": tx_msg["nonce"],
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data

def purchaseCTIFromBlockchain(wallet_id:str, password:str, cti_id:str)->tuple[str,bool]:
    """
        购买CTI
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            cti_id: CTI数据ID
        return:
            (str,bool): (结果信息,是否成功)
    """
    try:
        # 创建交易消息
        tx_msg = createCTIPurchaseTransaction(wallet_id, password, cti_id)
        
        # 构造请求数据
        tx_msg_data = {
            "user_id": str(tx_msg["user_id"]),
            "tx_data": tx_msg["tx_data"],
            "nonce": tx_msg["nonce"],
            "tx_signature": tx_msg["tx_signature"], 
            "nonce_signature": tx_msg["nonce_signature"]
        }

        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['cti']['purchaseCti'],
                               json=tx_msg_data)
        logging.info("purchaseCTIFromBlockchain response:"+str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False