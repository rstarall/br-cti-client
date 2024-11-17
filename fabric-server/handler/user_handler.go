package handler

import (
	"github.com/gin-gonic/gin"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	fabric "github.com/righstar2020/br-cti-client/fabric-server/fabric"
	global "github.com/righstar2020/br-cti-client/fabric-server/global"
)

func RegisterUserAccount(c *gin.Context){
	// 从请求中获取参数
	var params struct {
		WalletID  string `json:"wallet_id"`
		PublicPem string `json:"public_pem"` 
	}

	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(400, gin.H{"error": "参数错误"})
		return
	}

	// 调用链码注册用户账户
	client, err := fabric.CreateChannelClient(global.FabricSDK)
	if err != nil {
		c.JSON(500, gin.H{"error": "创建通道客户端失败"})
		return
	}

	// 准备调用链码的请求
	req := channel.Request{
		ChaincodeID: "user_chaincode",
		Fcn:         "registerUserInfo",
		Args:        [][]byte{[]byte(params.WalletID), []byte(params.PublicPem)},
	}

	// 执行链码
	resp, err := client.Execute(req)
	if err != nil {
		c.JSON(500, gin.H{"error": "执行链码失败:" + err.Error()})
		return
	}

	c.JSON(200, gin.H{
		"data": string(resp.Payload),
	})
}
