package fabric

import (
	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	"github.com/righstar2020/br-cti-client/fabric-server/global"
)

//获取交易nonce
func GetTransactionNonce(userID string, txSignature []byte) (string, error) {
	// 创建通道客户端
	client, err := CreateChannelClient(global.FabricSDK)
	if err != nil {
		return "", err
	}

	// 调用链码生成随机数
	req := channel.Request{
		ChaincodeID: "user_chaincode",
		Fcn:         "getTransactionNonce", 
		Args:        [][]byte{[]byte(userID), txSignature},
	}
	resp, err := client.Execute(req)
	if err != nil {
		return "", err
	}
	nonce := string(resp.Payload)
	return nonce, nil
}
