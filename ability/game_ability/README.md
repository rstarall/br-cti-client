# Game Ability - 博弈论防御策略计算模块

## 概述

Game Ability 模块提供了基于博弈论的网络防御策略计算功能，支持IP网络、5G网络和卫星网络三种场景的防御策略优化。

## 架构设计

本模块采用了类似 `ddos_ability` 的架构设计：

```
game_ability/
├── game_ability.py    # 核心业务逻辑类
├── app.py            # Flask API接口层
├── Attack.py         # 攻击策略计算模块
├── Defend.py         # 防御策略计算模块
├── demo.py           # 演示脚本
└── README.md         # 说明文档
```

## 核心类：GameAbility

### 主要功能

1. **IP网络防御策略计算** - `calculate_ip_strategy(input1, input2, input3)`
2. **5G网络防御策略计算** - `calculate_5g_strategy(budget)`
3. **卫星网络防御策略计算** - `calculate_satellite_strategy()`

### 返回格式

所有方法都返回统一的JSON格式：

```json
{
    "status": "success|error",
    "data": {
        "reduce": 29.0,           // 成本降低百分比
        "game_cost": 28.7,        // 博弈防御成本
        "single_cost": 40.4,      // 独立防御成本
        "input1": 15000,          // 输入参数（IP网络）
        "input2": 20000,          // 输入参数（IP网络）
        "input3": 25000,          // 输入参数（IP网络）
        "budget": 135000,         // 攻击预算（5G网络）
        "atrategy1": 49312,       // 攻击策略1（5G网络）
        "atrategy2": 50678,       // 攻击策略2（5G网络）
        "atrategy3": 51421,       // 攻击策略3（5G网络）
        "images": {
            "strategy1": "base64...", // 策略1饼图（base64编码）
            "strategy2": "base64...", // 策略2饼图（base64编码）
            "strategy3": "base64...", // 策略3饼图（base64编码）
            "attacker": "base64...",  // 攻击策略饼图（仅5G网络）
            "effect": "base64..."     // 效果对比柱状图（base64编码）
        }
    },
    "message": "错误信息"          // 仅在status为error时存在
}
```

## API接口

### 启动Flask应用

```bash
cd ability/game_ability
python app.py
```

应用将在 `http://localhost:5006` 启动。

### API端点

#### 1. IP网络策略计算

```http
POST /api/ip
Content-Type: application/json

{
    "input1": 15000,
    "input2": 20000,
    "input3": 25000
}
```

#### 2. 5G网络策略计算

```http
POST /api/5g
Content-Type: application/json

{
    "budget": 135000
}
```

#### 3. 卫星网络策略计算

```http
POST /api/satellite
Content-Type: application/json

{}
```

#### 4. 通用策略计算

```http
POST /api/strategy
Content-Type: application/json

{
    "strategy_type": "ip|5g|satellite",
    "input1": 15000,     // IP网络参数
    "input2": 20000,     // IP网络参数
    "input3": 25000,     // IP网络参数
    "budget": 135000     // 5G网络参数
}
```

## 使用示例

### Python代码示例

```python
from game_ability import GameAbility

# 创建实例
game_ability = GameAbility()

# 计算IP网络防御策略
result = game_ability.calculate_ip_strategy(15000, 20000, 25000)
if result["status"] == "success":
    print(f"成本降低: {result['data']['reduce']:.2f}%")

    # 获取图片base64数据
    images = result['data']['images']
    strategy1_base64 = images['strategy1']

    # 解码并保存图片
    import base64
    img_data = base64.b64decode(strategy1_base64)
    with open('strategy1.png', 'wb') as f:
        f.write(img_data)
```

### API调用示例

```python
import requests

# IP网络策略计算
response = requests.post('http://localhost:5006/api/ip',
                        json={"input1": 15000, "input2": 20000, "input3": 25000})
result = response.json()

if result["status"] == "success":
    print(f"成本降低: {result['data']['reduce']:.2f}%")
```

## 测试

### 运行单元测试

```bash
python tests/test_game_ability.py
```

### 运行API测试

```bash
python tests/test_api.py
```

## 与原有代码的兼容性

- 保留了原有的计算逻辑（`Attack.py`, `Defend.py`）
- 提供了纯API接口，支持程序化调用
- 图片生成改为返回base64编码，不再保存到文件系统
- 移除了Web界面和模板，专注于API服务

## 主要改进

1. **统一的接口设计** - 类似 `ddos_ability` 的架构
2. **返回base64图片** - 不依赖文件系统，支持分布式部署
3. **完善的错误处理** - 统一的错误返回格式
4. **纯API架构** - 专注于API服务，移除Web界面
5. **单元测试** - 完整的测试覆盖

## 依赖项

- Flask
- matplotlib
- scipy
- numpy (通过scipy间接依赖)

## 注意事项

1. 5G网络策略计算中的攻击策略优化可能失败，此时会使用平均分配策略
2. 防御策略计算失败时会使用默认策略（全部云清洗）
3. 图片生成使用中文字体，需要系统支持SimHei字体
4. 本模块专注于API服务，不提供Web界面
