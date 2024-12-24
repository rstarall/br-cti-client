
import requests
from blockchain.fabric import env_vars
from blockchain.fabric.tx import createTransaction
import logging
import json	
example_incentive_data = {
    "ref_id": "ref123",
    "doctype": "cti", 
    "mechanism": 1
}
def createIncentiveTransaction(wallet_id:str, password:str, incentive_data:dict)->dict:
    """
    创建激励交易
    params:
        wallet_id: 钱包ID
        password: 钱包密码
        incentive_data: 激励数据
    return:
        tx_msg_data: 交易消息
    """
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, incentive_data)
    
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"],
        "nonce": tx_msg["nonce"],
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data

def registerDocIncentiveInfo(wallet_id:str, password:str, incentive_data:dict)->tuple[str,bool]:
    """
    注册文档激励信息到区块链
    params:
        wallet_id: 钱包ID
        password: 钱包密码
        incentive_data: 激励数据
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 创建交易消息
        tx_msg_data = createIncentiveTransaction(wallet_id, password, incentive_data)
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['incentive']['registerDocIncentiveInfo'],
                               json=tx_msg_data)
        logging.info("registerDocIncentiveInfo response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def queryDocIncentiveInfo(ref_id:str, doc_type:str)->tuple[str,bool]:
    """
    查询文档激励信息
    params:
        ref_id: 关联ID
        doc_type: 文档类型
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        #发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['incentive']['queryDocIncentiveInfo'],
                               json={"ref_id": ref_id, "doc_type": doc_type})
        logging.info("queryDocIncentiveInfo response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False
