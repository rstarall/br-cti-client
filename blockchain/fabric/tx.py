import json
import requests
from blockchain.fabric import env_vars
from blockchain.user.signature import ecc_sign,ecc_sign_with_password
from blockchain.user.wallet import checkLocalUserAccountExist
import base64
def createTransaction(wallet_id:str,password:str,tx_data:dict)->dict:
    """
        创建交易(不需要验证签名)
        params:
            wallet_id: 钱包ID
            password: 钱包密码
            tx_data: 交易数据
        return:
            tx_msg: 交易消息
    """
    # 检查用户是否存在
    local_wallet_id = checkLocalUserAccountExist()
    if local_wallet_id != wallet_id:
        raise Exception("钱包ID不一致")
        
    # 处理交易数据
    #处理tx_data
    tx_data_bytes = json.dumps(tx_data).encode('utf-8')
    #base64编码
    tx_data_base64 = base64.b64encode(tx_data_bytes).decode('utf-8')
           
    # 构造交易消息
    tx_msg = {
        "user_id": wallet_id,
        "tx_data": tx_data_base64,          # 交易数据(Json base64 str)
        "tx_signature": "",  
        "nonce_signature": ""
    }
    
    return tx_msg

def createSignTransaction(wallet_id:str,password:str,tx_data:dict)->dict:
    """
        创建签名交易
        返回交易消息
        params:
            wallet_id:钱包ID
            password:钱包密码
            tx_data:交易数据->dict
        return:
            tx_msg:交易消息->dict
    """
    #检查用户是否存在   
    local_wallet_id = checkLocalUserAccountExist()
    if local_wallet_id != wallet_id:
        raise Exception("钱包ID不一致")
    
    #处理tx_data
    tx_data_bytes = json.dumps(tx_data).encode('utf-8')
    #base64编码
    tx_data_base64 = base64.b64encode(tx_data_bytes).decode('utf-8')
    #签名
    try:
        tx_signature,tx_data_bytes = ecc_sign_with_password(wallet_id, password, tx_data_base64)
    except Exception as e:
        raise Exception("签名失败")
    #获取nonce
    try:
        nonce = getTransactionNonce(wallet_id,tx_signature)
        #对nonce签名
        nonce_signature,nonce_bytes = ecc_sign_with_password(wallet_id, password, nonce)
    except Exception as e:
        raise Exception("获取nonce失败")
    
    # 交易消息基础结构(需要签名)
    tx_msg = {
        "user_id": wallet_id,           # 用户ID
        "tx_data": tx_data_bytes,          # 交易数据(Json bytes)
        "nonce": nonce,            # 随机数(base64)
        "tx_signature": tx_signature,     # 交易签名(Base64 ASN.1 DER)
        "nonce_signature": nonce_signature   # 随机数签名(Base64 ASN.1 DER)
    }
    return tx_msg


#交易调用接口
def getTransactionNonce(wallet_id:str,tx_signature:str)->str:
    """
        获取交易nonce
        根据钱包(用户)ID获取交易nonce
        params:
            wallet_id: 钱包(用户)ID
            tx_signature: 交易签名
        return:
            nonce: 交易nonce
    """
   
    # 构造请求参数
    data = {
        'user_id': wallet_id,
        'tx_signature': tx_signature
    }
    
    # 发送POST请求到fabric-server
    response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['tx']['getTransactionNonce'], json=data)
    
    if response.status_code != 200:
        raise Exception(response.json()['error'])
        
    return response.json()['result']
