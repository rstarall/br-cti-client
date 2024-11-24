package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/righstar2020/br-cti-client/fabric-server/fabric"
)

//CTI注册接口(Post)
func RegisterCtiInfo(c *gin.Context){
	// 解析请求参数
	ctiTxData := &fabric.CtiTxData{}
	if err := c.ShouldBindJSON(ctiTxData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	resp,err := fabric.RegisterCtiInfo(ctiTxData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

//CTI查询接口(Post)
func QueryCtiInfo(c *gin.Context){
	// 解析请求参数
	ctiTxData := &fabric.CtiTxData{}
	if err := c.ShouldBindJSON(ctiTxData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	resp,err := fabric.QueryCtiInfo(ctiTxData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

//根据ID和分页信息查询情报(Post)
func QueryCtiInfoByIDWithPagination(c *gin.Context) {
	// 解析请求参数
	var params struct {
		CtiIDPrefix string `json:"cti_id_prefix"`
		PageSize    int    `json:"page_size"`
		Bookmark    string `json:"bookmark"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryCtiInfoByIDWithPagination(params.CtiIDPrefix, params.PageSize, params.Bookmark)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

//根据类型查询情报(Post)
func QueryCtiInfoByType(c *gin.Context) {
	// 解析请求参数
	var params struct {
		CtiType int `json:"cti_type"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryCtiInfoByType(params.CtiType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

