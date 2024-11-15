
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
      print(blockInfo)
      return blockInfo,True
    except Exception as e:
      print(e)
      return None,False


def decode_block_txs(block):
    # 提取交易信息
    transactions = block['data']['data']

    # 遍历每个交易并提取交易 ID
    for tx in transactions:
        # 交易数据通常在 payload.data.action.proposal_response_payload 中
        if 'data' in tx['payload']:
            if 'actions' in tx['payload']['data']:
                for action_item in tx['payload']['data']['actions']:
                    proposal_response_payload = action_item['payload']['action']['proposal_response_payload']
                    proposal_response_payload_str=json.dumps(proposal_response_payload, indent=4)
                    print(proposal_response_payload_str)
        
        if 'header' in tx['payload']:
            # 解析 proposal_response_payload 以获取交易 ID
            transaction_id = tx['payload']['header']['channel_header']['tx_id']
            transaction_id = base64_to_binary(transaction_id).hex()
            print(f"Transaction ID: {transaction_id}")