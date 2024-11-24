package handler

import (
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/righstar2020/br-cti-client/fabric-server/fabric"
)

//查询情报统计信息
func QueryCTISummaryInfo(c *gin.Context) {
	// 解析请求参数
	var params struct {
		CtiID string `json:"cti_id"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	resp, err := fabric.QueryCTISummaryInfo(params.CtiID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}

//获取数据统计信息
func GetDataStatistics(c *gin.Context) {
	resp, err := fabric.GetDataStatistics()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": resp})
}