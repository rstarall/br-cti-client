import requests
from blockchain.fabric import env_vars
from blockchain.fabric.tx import createSignTransaction
import logging
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
        tx_msg = createSignTransaction(wallet_id, password, cti_data)
        
        # 构造请求参数
        data = {
            'chaincodeName': env_vars.chaincodeName,
            'function': env_vars.contract_invoke_functions['RegisterCTIInfo'],
            'args': tx_msg
        }
        
        # 发送POST请求到fabric-server
        response = requests.post(env_vars.fabricServerHost + env_vars.fabricServerApi['cti']['registerCtiInfo'], 
                               json=data)
        logging.info(response.json())
        if response.status_code != 200:
            return response.json()['error'], False
            
        return response.json()['data'], True
        
    except Exception as e:
        return str(e), False
