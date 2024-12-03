"""
    用户上链(注册)
    用户信息查询
"""
import json
import requests
from blockchain.fabric import env_vars
from blockchain.user.wallet import getUserPublicKey
from env.global_var import getUserWalletAbsolutePath
import os
userInfoExample = {
    "user_name":"admin",
    "public_key":"",
}

def updateLocalWalletOnchainStatus(wallet_id:str,onchain_wallet_id:str):
    """
    更新本地钱包上链状态
    """
    #获取本地钱包文件夹
    wallet_dir = getUserWalletAbsolutePath()+"/"+wallet_id
    new_wallet_dir = getUserWalletAbsolutePath()+"/"+onchain_wallet_id
    #修改文件夹名称为链上ID
    os.rename(wallet_dir,new_wallet_dir)
    #更新钱包文件夹中的onchain_status.json文件
    onchain_file_name = "wallet_status.json"
    with open(new_wallet_dir+"/"+onchain_file_name,"w") as f:
        json.dump({
            "onchain":True,
            "local_wallet_id":wallet_id,
            "onchain_wallet_id":onchain_wallet_id
        },f)

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
        onchain_wallet_id = response.json()['result']
        updateLocalWalletOnchainStatus(wallet_id,onchain_wallet_id)            
        return onchain_wallet_id, True
        
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
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def queryUserPointInfo(user_id: str) -> tuple[dict, bool]:
    """
    查询用户积分信息
    params:
        user_id: 用户ID
    return:
        result: 用户积分信息
        success: 是否成功
    """
    try:
        # 构造请求参数
        data = {
            "user_id": user_id
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['queryUserPointInfo'],
                               json=data)
                               
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False




def getUserStatistics(user_id: str) -> tuple[dict, bool]:
    """
    获取用户统计数据
    params:
        user_id: 用户ID
    return:
        result: 用户统计数据
        success: 是否成功
    """
    try:
        # 构造请求参数
        data = {
            "user_id": user_id
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['getUserStatistics'],
                               json=data)
                               
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False

def queryPointTransactions(user_id: str) -> tuple[dict, bool]:
    """
    查询用户积分交易记录
    params:
        user_id: 用户ID
    return:
        result: 积分交易记录
        success: 是否成功
    """
    try:
        # 构造请求参数
        data = {
            "user_id": user_id
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['user']['queryPointTransactions'],
                               json=data)
                               
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['result'], True
        
    except Exception as e:
        return str(e), False
