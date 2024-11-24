package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/righstar2020/br-cti-client/fabric-server/fabric"
)

// 注册模型信息(Post)
func RegisterModelInfo(c *gin.Context) {
	// 解析请求参数
	modelTxData := &fabric.ModelTxData{}
	if err := c.ShouldBindJSON(modelTxData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	resp, err := fabric.RegisterModelInfo(modelTxData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

// 查询模型信息(Post)
func QueryModelInfo(c *gin.Context) {
	// 解析请求参数
	var params struct {
		ModelID string `json:"model_id"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryModelInfo(params.ModelID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

// 根据ID和分页信息查询模型(Post)
func QueryModelInfoByIDWithPagination(c *gin.Context) {
	// 解析请求参数
	var params struct {
		ModelIDPrefix string `json:"model_id_prefix"`
		PageSize     int    `json:"page_size"`
		Bookmark     string `json:"bookmark"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryModelInfoByIDWithPagination(params.ModelIDPrefix, params.PageSize, params.Bookmark)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

// 根据流量类型查询模型(Post)
func QueryModelsByTrafficType(c *gin.Context) {
	// 解析请求参数
	var params struct {
		TrafficType string `json:"traffic_type"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryModelsByTrafficType(params.TrafficType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

// 根据CTI ID查询模型(Post)
func QueryModelsByRefCTIId(c *gin.Context) {
	// 解析请求参数
	var params struct {
		CTIID string `json:"cti_id"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryModelsByRefCTIId(params.CTIID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

// 根据创建者ID查询模型(Post)
func QueryModelInfoByCreatorUserID(c *gin.Context) {
	// 解析请求参数
	var params struct {
		UserID string `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryModelInfoByCreatorUserID(params.UserID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}
