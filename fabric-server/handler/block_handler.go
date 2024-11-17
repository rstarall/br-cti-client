package handler

import (
	"strconv"
	"net/http"
	"github.com/gin-gonic/gin"
	fabric "github.com/righstar2020/br-cti-client/fabric-server/fabric"
	global "github.com/righstar2020/br-cti-client/fabric-server/global"
)


func QueryBlockInfo(c *gin.Context){
	blockID := c.Param("blockID")
	id,_:=strconv.Atoi(blockID)
	block, err := fabric.QueryBlockInfo(global.LedgerClient,int64(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"code":200,"data":block})
}
func QueryChainInfo(c *gin.Context){
	info, err := fabric.QueryChainInfo(global.LedgerClient)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"code":200,"data":info})
}   
