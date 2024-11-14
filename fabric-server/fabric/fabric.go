package handler

import (
	"encoding/json"
	"errors"
	"fmt"
    "bytes"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/ledger"
	"github.com/hyperledger/fabric-sdk-go/pkg/common/logging"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
    "github.com/hyperledger/fabric-protos-go/common"
    "github.com/hyperledger/fabric/common/tools/protolator"
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
//创建通道上下文，可以执行链码
func CreateChannelClient(sdk *fabsdk.FabricSDK) (*channel.Client, error) {
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
func CreateLedgerClient(sdk *fabsdk.FabricSDK) (*ledger.Client, error) {
    // 获取通道上下文
    channelContext := sdk.ChannelContext("mychannel", fabsdk.WithUser("Admin"), fabsdk.WithOrg("Org1"))
    ledgerClient, err := ledger.New(channelContext)
    if err != nil {
        return nil, fmt.Errorf("failed to create new channel client: %v", err)
    }
    return ledgerClient, nil
}

//解析区块
func EncodeProto( input *common.Block) ([]byte,error) {
    var w = new(bytes.Buffer)
    if err := protolator.DeepMarshalJSON(w,input) ; err != nil {
        return nil,errors.New("error encoding output")
    }
    return w.Bytes(),nil
}



//链码执行请求
func InvokeChaincode(channelClient *channel.Client, chaincodeName, function string, args [][]byte) (string, error) {

    // 构建请求
    response, err := channelClient.Execute(channel.Request{ChaincodeID: chaincodeName, Fcn: function, Args: args})
    if err != nil {
        return "", err
    }

    return string(response.Payload), nil
}

//区块查询请求
func QueryBlockInfo(ledgerClient *ledger.Client, blockID int64) (string, error) {

    // 查询区块
    block, err := ledgerClient.QueryBlock(uint64(blockID))
    if err != nil {
        return "", err
    }

    // 将区块转换为可序列化的格式
    tree ,err := EncodeProto(block)
    if err != nil {
        return "",errors.New("error encoding block")
    }
    // // 将字节切片转换为 JSON
    // var blockMap map[string]interface{}
    // if err := json.Unmarshal(tree, &blockMap); err != nil {
    //     return "", errors.New("error converting block bytes to JSON")
    // }
    // // 使用 Indent 函数对 JSON 进行美化
    // prettyJSON, err := json.MarshalIndent(blockMap, "", "  ")
    // if err != nil {
    //     return "", errors.New("error indenting JSON")
    // }
    // return string(prettyJSON),nil
    return string(tree),nil
}
//查询最新区块
func QueryLatestBlockInfo(ledgerClient *ledger.Client, blockID int64) ([]byte, error) {
	
    // 查询区块
    block, err := ledgerClient.QueryBlock(0)
    if err != nil {
        return nil, err
    }

    // 将区块转换为可序列化的格式
    tree ,err := EncodeProto(block)
    if err != nil {
        return nil,errors.New("error encoding block")
    }
    jsonByte,err :=json.Marshal(tree)
    if err != nil {
        return nil,errors.New("error encoding block")
    }
    return jsonByte,nil
}
