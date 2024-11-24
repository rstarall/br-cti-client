package fabric

import (
	"github.com/righstar2020/br-cti-client/fabric-server/global"
)

//数据分析合约
//查询情报统计信息
func QueryCTISummaryInfo(ctiID string) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码查询情报统计信息
	resp, err := InvokeChaincode(client, "data_chaincode", "queryCTISummaryInfoByCTIID", [][]byte{[]byte(ctiID)})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}

//获取数据统计信息
func GetDataStatistics() (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码获取数据统计信息
	resp, err := InvokeChaincode(client, "data_chaincode", "getDataStatistics", [][]byte{})
	if err != nil {
		return "", err
	}
	return string(resp), nil
}
