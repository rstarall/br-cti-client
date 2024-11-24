package fabric

import (
	"encoding/json"
	"fmt"
	"github.com/righstar2020/br-cti-client/fabric-server/global"
)

// 模型合约

// 注册模型信息
func RegisterModelInfo(modelTxData *ModelTxData) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造注册消息数据
	msgJsonData, err := json.Marshal(modelTxData)
	if err != nil {
		return "", err
	}

	// 调用链码注册模型
	resp, err := InvokeChaincode(client, "model_chaincode", "registerModelInfo", [][]byte{[]byte(msgJsonData)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 查询模型信息
func QueryModelInfo(modelID string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码查询模型
	resp, err := InvokeChaincode(client, "model_chaincode", "queryModelInfo", [][]byte{[]byte(modelID)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据ID和分页信息查询模型
func QueryModelInfoByIDWithPagination(modelIDPrefix string, pageSize int, bookmark string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 构造查询参数
	args := [][]byte{
		[]byte(modelIDPrefix),
		[]byte(fmt.Sprintf("%d", pageSize)),
		[]byte(bookmark),
	}

	// 调用链码查询模型
	resp, err := InvokeChaincode(client, "model_chaincode", "queryModelInfoByModelIDWithPagination", args)
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据流量类型查询模型
func QueryModelsByTrafficType(trafficType string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码查询模型
	resp, err := InvokeChaincode(client, "model_chaincode", "queryModelsByTrafficType", [][]byte{[]byte(trafficType)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据CTI ID查询模型
func QueryModelsByRefCTIId(ctiID string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码查询模型
	resp, err := InvokeChaincode(client, "model_chaincode", "queryModelsByRefCTIId", [][]byte{[]byte(ctiID)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

// 根据创建者ID查询模型
func QueryModelInfoByCreatorUserID(userID string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码查询模型
	resp, err := InvokeChaincode(client, "model_chaincode", "queryModelInfoByCreatorUserID", [][]byte{[]byte(userID)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}
