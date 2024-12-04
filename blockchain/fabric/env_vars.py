#全局配置
#智能合约名称
chaincodeName = "br-cti-contract"

#智能合约查询函数(无需签名)
contract_query_functions = {
    "RegisterUserInfo":"RegisterUserInfo", #用户注册(无需签名)
    "GetUserInfo":"GetUserInfo", #查询用户信息(无需签名)
    "GetCTIInfo":"GetCTIInfo", #查询CTI信息(无需签名)
    "GetModelInfo":"GetModelInfo", #查询模型信息(无需签名)
    "QueryModelsByTrafficType":"QueryModelsByTrafficType", #根据流量类型查询模型
    "QueryModelsByRefCTIId":"QueryModelsByRefCTIId", #根据相关CTI查询模型
    "QueryCTIInfoByType":"QueryCTIInfoByType", #根据类型查询CTI
    "QueryCTISummaryInfoByCTIID":"QueryCTISummaryInfoByCTIID", #查询CTI摘要信息
    "GetDataStatistics":"GetDataStatistics" #获取数据统计信息
}

#智能合约函数(需要签名)
contract_invoke_functions = {
   "RegisterCTIInfo":"RegisterCTIInfo", #CTI注册
   "RegisterModelInfo":"RegisterModelInfo", #模型注册
   "PurchaseCTI":"PurchaseCTI", #购买CTI
   "GetTransactionNonce":"GetTransactionNonce" #获取交易随机数
}


#fabric-server地址
fabricServerHost = "http://localhost:7777"

#fabric-server接口
fabricServerApi = {
    "blockchain":{
        "queryBlock": "/blockchain/queryBlock",
        "queryChain": "/blockchain/queryChain"
    },
    "contract":{
        "queryContract": "/contract/queryContract",
        "invokeContract": "/contract/invokeContract"
    },
    "tx":{
        "getTransactionNonce": "/tx/getTransactionNonce"
    },
    "user":{
        "registerUserAccount": "/user/registerUserAccount",
        "queryUserInfo": "/user/queryUserInfo",
        "getUserCTIStatistics": "/user/getUserStatistics"
    },
    "cti":{
        "registerCtiInfo": "/cti/registerCtiInfo", 
        "queryCtiInfo": "/cti/queryCtiInfo",
        "queryCtiInfoByIDWithPagination": "/cti/queryCtiInfoByIDWithPagination",
        "queryCtiInfoByType": "/cti/queryCtiInfoByType"
    },
    "model":{
        "registerModelInfo": "/model/registerModelInfo",
        "queryModelInfo": "/model/queryModelInfo",
        "queryModelInfoByIDWithPagination": "/model/queryModelInfoByIDWithPagination",
        "queryModelsByTrafficType": "/model/queryModelsByTrafficType",
        "queryModelsByRefCTIId": "/model/queryModelsByRefCTIId",
        "queryModelInfoByCreatorUserID": "/model/queryModelInfoByCreatorUserID"
    },
    "dataStat":{
        "queryCTISummaryInfo": "/dataStat/queryCTISummaryInfo",
        "getDataStatistics": "/dataStat/getDataStatistics"
    }
}
