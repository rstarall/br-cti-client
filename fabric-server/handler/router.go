package handler

import (
	"github.com/gin-gonic/gin"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
)
func NewRouter(fabricSDK *fabsdk.FabricSDK) *gin.Engine {
	r := gin.New()
    blockchainApi := r.Group("/blockchain")
    {
        // 查询区块信息
        blockchainApi.Any("/queryBlock/:blockID", QueryBlockInfo)
        //查询区块链信息
        blockchainApi.Any("/queryChain", QueryChainInfo)
    }
    contractApi := r.Group("/contract") 
    {
        // 调用智能合约
        contractApi.POST("/queryContract", QueryContract)
        contractApi.POST("/invokeContract", InvokeContract)
    }
    txApi := r.Group("/tx")
    {
        //获取交易nonce
        txApi.POST("/getTransactionNonce", GetTxNonce)
    }
    userApi := r.Group("/user")
    {
        //用户链上接口
        userApi.POST("/registerUserAccount", RegisterUserAccount)
        userApi.POST("/queryUserInfo", QueryUserInfo)
    }
    ctiApi := r.Group("/cti")
    {
        //CTI接口
        ctiApi.POST("/registerCtiInfo", RegisterCtiInfo)
        ctiApi.POST("/queryCtiInfo", QueryCtiInfo)
        ctiApi.POST("/queryCtiInfoByIDWithPagination", QueryCtiInfoByIDWithPagination)
        ctiApi.POST("/queryCtiInfoByType", QueryCtiInfoByType)
    }
    modelApi := r.Group("/model")
    {
        //模型接口
        modelApi.POST("/registerModelInfo", RegisterModelInfo)
        modelApi.POST("/queryModelInfo", QueryModelInfo)
        modelApi.POST("/queryModelInfoByIDWithPagination", QueryModelInfoByIDWithPagination)
        modelApi.POST("/queryModelsByTrafficType", QueryModelsByTrafficType)
        modelApi.POST("/queryModelsByRefCTIId", QueryModelsByRefCTIId)
        modelApi.POST("/queryModelInfoByCreatorUserID", QueryModelInfoByCreatorUserID)
    }   
    dataStatApi := r.Group("/dataStat")
    {
        //数据分析接口
        dataStatApi.POST("/queryCTISummaryInfo", QueryCTISummaryInfo)
        dataStatApi.POST("/getDataStatistics", GetDataStatistics)
    }
	return r
}
