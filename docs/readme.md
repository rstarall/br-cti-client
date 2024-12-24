# 1.Client 端介绍

## 1.1 目录结构

```
.
├── bc-server/                # 区块链服务器端
├── blockchain/              # 区块链相关实现
│   ├── fabric/             # Hyperledger Fabric实现
│   │   ├── block.py        # 区块处理
│   │   ├── comment.py      # 评论相关
│   │   ├── contract.py     # 智能合约调用
│   │   ├── cti_onchain.py  # CTI上链
│   │   ├── data_stat.py    # 数据统计
│   │   ├── env_vars.py     # 环境变量
│   │   ├── incentive.py    # 激励机制
│   │   ├── ml_onchain.py   # 机器学习模型上链
│   │   ├── msg.py         # 消息结构定义
│   │   ├── tx.py          # 交易处理
│   │   └── user_onchain.py # 用户上链
│   ├── ipfs/               # IPFS实现
│   │   └── ipfs.py        # IPFS接口实现
│   ├── user/               # 用户相关
│   │   ├── signature.py    # 签名处理
│   │   └── wallet.py       # 钱包管理
│   └── wallet/             # 钱包数据存储
├── data/                   # 数据处理
│   ├── extensions_data.py  # 扩展数据处理
│   ├── feature_mapping.csv # 特征映射配置
│   ├── stix_process.py    # STIX格式处理
│   └── traffic_data.py    # 流量数据处理
├── db/                     # 数据库
│   ├── db.json            # 数据库文件
│   └── tiny_db.py         # TinyDB封装
├── docs/                   # 文档
│   ├── dev.md             # 开发说明
│   ...
├── env/                    # 环境配置
│   └── global_var.py      # 全局变量
├── ml/                     # 机器学习
│   ├── evaluate_model.py  # 模型评估
│   ├── ml_model.py        # 模型管理
│   ├── model_plot.py      # 模型可视化
│   ├── model_progress.py  # 训练进度
│   ├── model_status.py    # 模型状态
│   ├── precess_data.py    # 数据预处理
│   └── train_model.py     # 模型训练
├── server/                 # 服务器
│   ├── app.py             # Flask应用
│   └── handler/           # 请求处理
│       ├── bc_handler.py      # 区块链处理
│       ├── comment_handler.py # 评论处理
│       ├── data_handler.py    # 数据处理
│       ├── incentive_handler.py # 激励处理
│       ├── index_handler.py   # 首页处理
│       ├── ml_handler.py      # 机器学习处理
│       ├── upchain_handler.py # 上链处理
│       └── user_handler.py    # 用户处理
├── util/                   # 工具类
│   ├── file.go            # 文件操作工具
│   └── util.go            # 通用工具函数
└── service/               # 业务服务
    ├── bc_service.py     # 区块链服务
    ├── data_service.py   # 数据服务
    ├── kp_service.py     # 知识平面服务
    ├── ml_service.py     # 机器学习服务
    ├── model/            # 数据模型
    │   ├── cti_model.py  # CTI数据结构
    │   ├── ml_model.py   # 机器学习模型结构
    │   └── stix_model.py # STIX模型结构
    └── wallet_service.py # 钱包服务
```
