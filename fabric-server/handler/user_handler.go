package handler

import (
	"github.com/gin-gonic/gin"
	fabric "github.com/righstar2020/br-cti-client/fabric-server/fabric"
)

func RegisterUserAccount(c *gin.Context){
	// 从请求中获取参数
	var params struct {
		UserName  string `json:"user_name"`
		PublicKey string `json:"public_key"` 
	}

	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(400, gin.H{"error": "参数错误"})
		return
	}

	resp, err := fabric.RegisterUserAccount(params.UserName, params.PublicKey)
	if err != nil {
		c.JSON(500, gin.H{"error": "执行链码失败:" + err.Error()})
		return
	}

	c.JSON(200, gin.H{
		"code": 200,
		"data": resp,
	})
}

func QueryUserInfo(c *gin.Context) {
	// 从请求中获取参数
	var params struct {
		UserID string `json:"user_id"`
	}

	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(400, gin.H{"error": "参数错误"})
		return
	}

	resp, err := fabric.QueryUserInfo(params.UserID)
	if err != nil {
		c.JSON(500, gin.H{"error": "查询用户信息失败:" + err.Error()})
		return
	}

	c.JSON(200, gin.H{
		"code": 200,
		"data": resp,
	})
}

