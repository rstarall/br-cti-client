package fabric

import (
	"encoding/json"
	"fmt"
	"github.com/righstar2020/br-cti-client/fabric-server/global"
)

//情报合约
//注册情报
func RegisterCtiInfo(ctiTxData *CtiTxData) (string, error) {
	// 调用链码注册情报
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造注册消息数据
	msgJsonData, err := json.Marshal(ctiTxData)
	if err != nil {
		return "", err
	}

	resp, err := InvokeChaincode(client, "cti_chaincode", "registerCtiInfo", [][]byte{[]byte(msgJsonData)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

//查询情报
func QueryCtiInfo(ctiTxData *CtiTxData) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造查询消息数据
	msgJsonData, err := json.Marshal(ctiTxData)
	if err != nil {
		return "", err
	}

	// 调用链码查询情报
	resp, err := InvokeChaincode(client, "cti_chaincode", "queryCTIInfo", [][]byte{[]byte(msgJsonData)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据ID和分页信息查询情报
func QueryCtiInfoByIDWithPagination(ctiIDPrefix string, pageSize int, bookmark string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造查询参数
	args := [][]byte{
		[]byte(ctiIDPrefix),
		[]byte(fmt.Sprintf("%d", pageSize)),
		[]byte(bookmark),
	}

	// 调用链码查询情报
	resp, err := InvokeChaincode(client, "cti_chaincode", "queryCTIInfoByCTIIDWithPagination", args)
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据类型查询情报
func QueryCtiInfoByType(ctiType int) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造查询参数
	args := [][]byte{
		[]byte(fmt.Sprintf("%d", ctiType)),
	}

	// 调用链码查询情报
	resp, err := InvokeChaincode(client, "cti_chaincode", "queryCTIInfoByType", args)
	if err != nil {
		return "", err
	}
	return string(resp), nil
}
