package fabric
//数据传输结构
//不需要签名的消息
type UserRegisterMsgData struct {
	UserName string `json:"user_name" default:""` //用户名称
	PublicKey string `json:"public_key" default:""` //用户公钥(pem string)
}
//交易数据结构(需要签名的数据)
type TxMsgData struct {
	UserID string `json:"user_id"` //用户ID
	TxData []byte `json:"tx_data"` //交易数据
	Nonce string `json:"nonce"` //随机数(base64)
	TxSignature []byte `json:"tx_signature"` //交易签名(Base64 ASN.1 DER)
	NonceSignature []byte `json:"nonce_signature"` //随机数签名(Base64 ASN.1 DER)
}
//情报交易数据结构
type CtiTxData struct {
	CTIID          string   `json:"cti_id"`           // 情报ID(链上生成)
	CTIHash        string   `json:"cti_hash"`         // 情报HASH(sha256链下生成)
	CTIName        string   `json:"cti_name"`         // 情报名称(可为空)
	CTIType        int      `json:"cti_type"`         // 情报类型（1:恶意流量、2:恶意软件、3:钓鱼地址、4:僵尸网络、5:应用层攻击、6:开源情报）
	CTITrafficType int      `json:"cti_traffic_type"` // 流量情报类型（0:非流量、1:5G、2:卫星网络、3:SDN）
	OpenSource     int      `json:"open_source"`      // 是否开源（0不开源，1开源）
	CreatorUserID  string   `json:"creator_user_id"`  // 创建者ID(公钥sha256)
	Tags           []string `json:"tags"`             // 情报标签数组
	IOCs           []string `json:"iocs"`             // 包含的沦陷指标（IP, Port, URL, Hash）
	StixData       []byte   `json:"stix_data"`        // STIX数据（JSON []byte）可以有多条
	StatisticInfo  []byte   `json:"statistic_info"`   // 统计信息(JSON []byte)
	Description    string   `json:"description"`      // 情报描述
	DataSize       int      `json:"data_size"`        // 数据大小（B）
	DataHash       string   `json:"data_hash"`        // 情报数据HASH（sha256）
	IPFSHash       string   `json:"ipfs_hash"`        // IPFS地址
	Need           int      `json:"need"`             // 情报需求量(销售数量)
	Value          int      `json:"value"`            // 情报价值（积分）
	CompreValue    int      `json:"compre_value"`     // 综合价值（积分激励算法定价）
	CreateTime     string   `json:"create_time"`      // 情报创建时间（由合约生成）
}

type PurchaseCtiTxData struct {
	CTIID string `json:"cti_id"` // 情报ID
	UserID string `json:"user_id"` // 用户ID
}

//模型交易数据结构
type ModelTxData struct {
	ModelID          string   `json:"model_id"`           // 模型ID
	ModelHash        string   `json:"model_hash"`         // 模型hash
	ModelName        string   `json:"model_name"`         // 模型名称
	ModelType        int      `json:"model_type"`         // 模型类型
	ModelTrafficType int      `json:"model_traffic_type"` // 流量模型类型
	ModelOpenSource  int      `json:"model_open_source"`  // 是否开源
	ModelFeatures    []string `json:"model_features"`     // 模型特征
	ModelTags        []string `json:"model_tags"`         // 模型标签
	ModelDescription string   `json:"model_description"`  // 模型描述
	ModelDataSize    int      `json:"model_data_size"`    // 数据大小
	ModelIPFSHash    string   `json:"model_ipfs_hash"`    // IPFS地址
}
