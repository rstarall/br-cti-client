package handler

import (
	"github.com/gin-gonic/gin"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
)
func NewRouter(fabricSDK *fabsdk.FabricSDK) *gin.Engine {
	r := gin.New()
    // 查询区块信息
    r.Any("/queryBlock/:blockID", QueryBlockInfo)
    //查询区块链信息
    r.Any("/queryChain", QueryChainInfo)
    // 调用链代码
    r.POST("/registerUserAccount", RegisterUserAccount)
    r.POST("/getTransactionNonce", GetTransactionNonce)
	return r
}

