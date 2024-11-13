package handler

import (
	"encoding/json"
	"errors"
	"fmt"

	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/ledger"
	"github.com/hyperledger/fabric-sdk-go/pkg/common/logging"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
)

func NewSDK(configPath string) (*fabsdk.FabricSDK, error) {
    // 设置日志级别
    logging.SetLevel("fabsdk", 4)
    
    // 加载配置文件
    config := config.FromFile(configPath)
    
    // 创建新的SDK实例
    sdk, err := fabsdk.New(config)
    if err != nil {
        return nil, fmt.Errorf("failed to create new SDK: %v", err)
    }
    return sdk, nil
}
func createChannelClient(sdk *fabsdk.FabricSDK) (*channel.Client, error) {
    // 获取通道上下文
    channelContext := sdk.ChannelContext("mychannel", fabsdk.WithUser("Admin"), fabsdk.WithOrg("Org1"))
    
    // 创建通道客户端
    client, err := channel.New(channelContext)
    if err != nil {
        return nil, fmt.Errorf("failed to create new channel client: %v", err)
    }
    return client, nil
}
// 创建ledger客户端（查询区块链状态）
func createLedgerClient(sdk *fabsdk.FabricSDK) (*ledger.Client, error) {
    // 获取通道上下文
    channelContext := sdk.ChannelContext("mychannel", fabsdk.WithUser("Admin"), fabsdk.WithOrg("Org1"))
    lederClient, err := ledger.New(channelContext)
    if err != nil {
        return nil, fmt.Errorf("failed to create new channel client: %v", err)
    }
    return lederClient, nil
}

// //解析区块
// func EncodeProto( input *common.Block) ([]byte,error) {
//     var w = new(bytes.Buffer)
//     if err := protolator.DeepMarshalJSON(w,input) ; err != nil {
//         return nil,errors.New("error encoding output")
//     }
//     return w.Bytes(),nil
// }



//链码执行请求
func InvokeChaincode(sdk *fabsdk.FabricSDK, chaincodeName, function string, args [][]byte) (string, error) {
    // 创建通道客户端
    channelClient, err := createChannelClient(sdk)
    if err != nil {
        return "", err
    }

    // 构建请求
    response, err := channelClient.Execute(channel.Request{ChaincodeID: chaincodeName, Fcn: function, Args: args})
    if err != nil {
        return "", err
    }

    return string(response.Payload), nil
}

//区块查询请求
func QueryBlockInfo(sdk *fabsdk.FabricSDK, blockID int64) ([]byte, error) {
    // 创建通道客户端
    ledgerClient, err := createLedgerClient(sdk)
    if err != nil {
        return nil, err
    }
	
    // 查询区块
    block, err := ledgerClient.QueryBlock(uint64(blockID))
    if err != nil {
        return nil, err
    }

    // 将区块转换为可序列化的格式
	// tree ,err := EncodeProto(block)
    // tree ,err := EncodeProto(block)
    jsonByte,err :=json.Marshal(block)
    if err != nil {
        return nil,errors.New("error encoding block")
    }
    return jsonByte,nil
}

