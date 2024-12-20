import requests
from blockchain.fabric import env_vars
from blockchain.fabric.tx import createTransaction
import logging
import json
example_comment_data = {
    # "comment_id": "1234567890",
    # "user_id": "user123",
    # "user_level": 1,
    "comment_doc_type": "cti", 
    "comment_ref_id": "ref123",
    "comment_score": 4.5,
    "comment_content": "这是一条评论",
    # "comment_status": 1,
    # "create_time": "2024-01-01 00:00:00",
    # "doctype": "comment"
}
def createCommentTransaction(wallet_id:str, password:str, comment_data:dict)->dict:
    """
        创建评论交易
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            comment_data: 评论数据
        return:
            tx_msg_data: 交易消息
    """
    # 创建交易消息
    tx_msg = createTransaction(wallet_id, password, comment_data)
    
    tx_msg_data = {
        "user_id": str(tx_msg["user_id"]),
        "tx_data": tx_msg["tx_data"],
        "nonce": tx_msg["nonce"], 
        "tx_signature": tx_msg["tx_signature"],
        "nonce_signature": tx_msg["nonce_signature"]
    }
    return tx_msg_data

def registerComment(wallet_id:str, password:str, comment_data:dict)->tuple[str,bool]:
    """
        注册评论到区块链
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            comment_data: 评论数据
        return:
            result: 结果信息
            success: 是否成功
    """
    try:
        # 创建交易消息
        tx_msg_data = createCommentTransaction(wallet_id, password, comment_data)
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['comment']['registerComment'],
                               json=tx_msg_data)
        logging.info("registerComment response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def approveComment(wallet_id:str, password:str, comment_id:str)->tuple[str,bool]:
    """
    审核评论
    params:
        wallet_id: 钱包ID
        password: 钱包密码
        comment_id: 评论ID
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 创建交易消息
        tx_msg_data = createCommentTransaction(wallet_id, password, {"comment_id": comment_id})
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['comment']['approveComment'],
                               json=tx_msg_data)
        logging.info("approveComment response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def queryComment(comment_id:str)->tuple[str,bool]:
    """
    查询单个评论
    params:
        comment_id: 评论ID
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 发送GET请求到fabric-server
        response = requests.get(env_vars.fabricServerHost + env_vars.fabricServerApi['comment']['queryComment'],
                              params={"comment_id": comment_id})
        logging.info("queryComment response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False
def queryAllCommentsByRefID(ref_id:str)->tuple[str,bool]:
    """
    查询所有评论列表
    params:
        ref_id: 关联ID
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['comment']['queryAllCommentsByRefID'],
                               json={"ref_id": ref_id})
        logging.info("queryAllCommentsByRefID response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def queryCommentsByRefID(ref_id:str, page:int, page_size:int)->tuple[str,bool]:
    """
    分页查询评论列表
    params:
        ref_id: 关联ID
        page: 页码
        page_size: 每页大小
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['comment']['queryCommentsByRefID'],
                               json={"ref_id": ref_id, "page": page, "page_size": page_size})
        logging.info("queryCommentsByRefID response:" + str(response.json()))
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False
