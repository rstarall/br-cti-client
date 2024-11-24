package fabric

import (
	"bytes"
	"encoding/json"
	// "encoding/json"
	"errors"
	"fmt"
	"strings"

	"github.com/hyperledger/fabric-protos-go/common"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/ledger"
	"github.com/hyperledger/fabric-sdk-go/pkg/common/logging"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
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





//链码执行请求
func InvokeChaincode(channelClient *channel.Client, chaincodeName, function string, args [][]byte) ([]byte, error) {

    // 构建请求
    response, err := channelClient.Execute(channel.Request{
		ChaincodeID: chaincodeName, 
		Fcn:         function,
		Args:        args,
	},)
    if err != nil {
        return nil, err
    }

    return response.Payload, nil
}


//解析区块
func EncodeProto( input *common.Block) ([]byte,error) {
    var w = new(bytes.Buffer)
    if err := protolator.DeepMarshalJSON(w,input) ; err != nil {
        return nil,errors.New("error encoding output")
    }
    return w.Bytes(),nil
}

//区块查询请求
func QueryBlockInfo(ledgerClient *ledger.Client, blockID int64) (string, error) {

    // 查询区块
    block, err := ledgerClient.QueryBlock(uint64(blockID))
    if err != nil {
        return "", err
    }

    // 将区块转换为可序列化的格式
    treeBytes ,err := EncodeProto(block)
    if err != nil {
        return "",errors.New("error encoding block")
    }
	jsonStr := strings.ReplaceAll(string(treeBytes), "\t", "")
    jsonStr = strings.ReplaceAll(jsonStr, "\n", "")
    return jsonStr,nil
}

//区块链信息
func QueryChainInfo(ledgerClient *ledger.Client) (string, error) {

    // 查询区块
    infoResp, err := ledgerClient.QueryInfo()
    if err != nil {
        return "", err
    }
    jsonStr,err := json.Marshal(infoResp)
    if err != nil {
        return "", err
    }
    return string(jsonStr),nil
}
