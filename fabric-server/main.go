package main

import (
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
	"fmt"
)
var  fabricSDK *fabsdk.FabricSDK
func main() {
    // 启动Fabric SDK
    fabricSDK, err := newSDK("./config/config.yaml") // 确保路径正确
    if err != nil {
        fmt.Printf("Failed to initialize SDK: %v", err)
    }
    defer fabricSDK.Close()

    r := NewRouter()
    // 启动服务
    if err := r.Run(":8080"); err != nil {
        fmt.Printf("Failed to start server: %v", err)
    }
}
