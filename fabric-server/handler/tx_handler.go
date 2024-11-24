package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/righstar2020/br-cti-client/fabric-server/fabric"
)

//获取交易nonce接口
func GetTxNonce(c *gin.Context) {
	// 解析请求参数
	var params struct {
		UserID      string `json:"user_id"`
		TxSignature []byte `json:"tx_signature"` 
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	nonce, err := fabric.GetTransactionNonce(params.UserID, params.TxSignature)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": nonce})
}
