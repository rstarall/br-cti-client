package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
    "strconv"
    "github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
    fabric "github.com/righstar2020/br-cti-client/fabric-server/fabric"
)
func NewRouter(fabricSDK *fabsdk.FabricSDK) *gin.Engine {
	r := gin.New()
	// 调用链代码
    r.POST("/invoke", func(c *gin.Context) {
        // 实现调用逻辑
        args:=c.PostFormArray("args")
        var params [][]byte
        for i := 0; i < len(args); i++ {
            params = append(params,[]byte(args[i]))
        }
        resp, err := fabric.InvokeChaincode(fabricSDK, c.PostForm("chaincodeName"), c.PostForm("function"), params)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        c.JSON(http.StatusOK, gin.H{"result": resp})
    })

    // 查询区块信息
    r.GET("/queryBlock/:blockID", func(c *gin.Context) {
        blockID := c.Param("blockID")
        id,_:=strconv.Atoi(blockID)
        block, err := fabric.QueryBlockInfo(fabricSDK,int64(id))
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        c.JSON(http.StatusOK, gin.H{"block": block})
    })
	return r
}

