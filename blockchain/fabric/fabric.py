
"""
   Fabric接口实现
   如网络连接等，
   需要config配置文件
"""
#通过Web接口调用fabric-server

import json
from utils.request import request_get
from env.global_var import fabricServerHost
from utils.base64 import base64_to_binary
def checkBlockchainStatus():
    try:
      blockInfo = request_get(fabricServerHost+"/queryChain")
      if blockInfo==None:
        return None,False
      return blockInfo,True
    except Exception as e:
      print(e)
      return None,False
def getBlockByHeight(height):
   try:
      response = request_get(fabricServerHost+"/queryBlock/"+str(height))
      if response == None:
         return None,False
      if "error" in response:
        return response["error"],False
      
      rawBlockInfo = json.loads(response["data"])
      blockInfo = process_block_info(rawBlockInfo)
      return blockInfo,True
   except Exception as e:
      print(e)
      return None,False

def process_block_info(block):
    blockInfo = {
       "height":0,
       "block_hash":"",
       "prev_hash":"",
       "tx_num":0,
       "transactions":[],
    }
    #提取区块信息
    if "header" in block:
       blockInfo["height"] = block['header']['number']
       blockInfo["block_hash"]=base64_to_binary(block['header']['data_hash']).hex()
       blockInfo["prev_hash"]=base64_to_binary(block['header']['previous_hash']).hex()
       blockInfo["tx_num"]=len(block['data']['data'])
    # 提取交易信息
    transactions = []
    if "data" in block:
       if "data" in block['data']:
            transactions = block['data']['data']
    # 遍历每个交易并提取交易 ID
    for tx in transactions:
        tx_info = {
           "tx_id":"",
           "tx_data":"",
           "signature":"",
        }
        if 'payload' in tx:
            print(tx['payload'])
            # 交易数据通常在 payload.data.action.proposal_response_payload 中
            if 'data' in tx['payload']:
                if 'actions' in tx['payload']['data']:
                    for action_item in tx['payload']['data']['actions']:
                        proposal_response_payload = action_item['payload']['action']['proposal_response_payload']
                    
                        tx_info["tx_data"]=proposal_response_payload
            
            if 'header' in tx['payload']:
                # 解析 proposal_response_payload 以获取交易 ID
                transaction_id = tx['payload']['header']['channel_header']['tx_id']
                transaction_id = base64_to_binary(transaction_id).hex()
                print(f"Transaction ID: {transaction_id}")
                tx_info["tx_id"]=transaction_id
                
        if 'signature' in tx:
            signature = tx['signature']
            tx_info["signature"]=signature    
        blockInfo["transactions"].append(tx_info)
    return blockInfo