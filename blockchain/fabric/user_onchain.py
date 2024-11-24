"""
    用户上链(注册)
    用户信息查询
"""
import json
import requests
from blockchain.fabric import env_vars
from blockchain.user.wallet import getUserPublicKey

userInfoExample = {
    "user_name":"admin",
    "public_key":"",
}

def registerUserOnchain(wallet_id:str, user_name:str="")->tuple[str,bool]:
    """
    使用公钥注册用户账户
    params:
        wallet_id: 用户钱包ID
        user_name: 用户名称(可选)
    return:
        result: 结果信息
        success: 是否成功
    """
    try:
        # 获取用户公钥
        public_key = getUserPublicKey(wallet_id)
        
        # 构造请求参数
        data = {
            "user_name": user_name,
            "public_key": public_key
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['registerUserAccount'], 
                               json=data)
        
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['data'], True
        
    except Exception as e:
        return str(e), False

def queryUserInfo(user_id:str)->tuple[dict,bool]:
    """
    查询用户信息
    params:
        user_id: 用户ID
    return:
        result: 用户信息
        success: 是否成功
    """
    try:
        # 构造请求参数
        data = {
            "user_id": user_id
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['queryUserInfo'],
                               json=data)
                               
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['data'], True
        
    except Exception as e:
        return str(e), False
