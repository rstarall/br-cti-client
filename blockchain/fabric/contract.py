from blockchain.fabric import env_vars
import requests
#直接调用接口执行合约

def query_contract(function_name:str,args:dict)->dict:
    """
        调用智能合约查询类函数(不需要调用者签名)
        :param chaincode_name:合约名称
        :param function_name:函数名称
        :param args:参数列表
        :return 返回值
    """
    
    
    # 构造请求参数
    data = {
        'chaincodeName': env_vars.chaincodeName,
        'function': function_name,
        'args': args
    }
    
    # 发送POST请求到fabric-server
    response = requests.post('http://localhost:8080/queryContract', data=data)
    
    if response.status_code != 200:
        raise Exception(response.json()['error'])
        
    return response.json()['result']


def invoke_contract(function_name:str,args:dict)->dict:
    """
        调用智能合约函数
        :param chaincode_name:合约名称
        :param function_name:函数名称
        :param args:参数列表
        :return 返回值
    """
    import requests
    
    # 构造请求参数
    data = {
        'chaincodeName': env_vars.chaincodeName,
        'function': function_name,
        'args': args
    }
    
    # 发送POST请求到fabric-server
    response = requests.post('http://localhost:8080/invokeContract', data=data)
    
    if response.status_code != 200:
        raise Exception(response.json()['error'])
        
    return response.json()['result']

