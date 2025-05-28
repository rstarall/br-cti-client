# 博弈论防御策略计算服务 API 文档

## 概述

`game_handler.py` 提供了基于博弈论的网络防御策略计算服务，支持IP网络、5G网络和卫星网络三种场景的防御策略优化。

## 服务架构

- **模块路径**: `server/handler/game_handler.py`
- **蓝图名称**: `game`
- **URL前缀**: `/game`
- **核心服务**: `GameAbility` 类

## API 接口

### 1. IP网络防御策略计算

**接口地址**: `/game/ip_strategy`

**支持方法**: `GET`, `POST`

**参数说明**:
- `input1`: 对节点1的攻击流量 (数值类型，非负)
- `input2`: 对节点2的攻击流量 (数值类型，非负)  
- `input3`: 对节点3的攻击流量 (数值类型，非负)

**请求示例**:

GET请求:
```
GET /game/ip_strategy?input1=1000&input2=1500&input3=2000
```

POST请求:
```json
POST /game/ip_strategy
Content-Type: application/json

{
    "input1": 1000,
    "input2": 1500,
    "input3": 2000
}
```

**响应格式**:

成功响应 (200):
```json
{
    "status": "success",
    "data": {
        "reduce": 15.5,
        "game_cost": 8450.0,
        "single_cost": 10000.0,
        "input1": 1000,
        "input2": 1500,
        "input3": 2000,
        "images": {
            "strategy1": "base64编码的策略1饼图",
            "strategy2": "base64编码的策略2饼图",
            "strategy3": "base64编码的策略3饼图",
            "effect": "base64编码的效果对比柱状图"
        }
    }
}
```

失败响应 (400):
```json
{
    "error": "错误信息",
    "data": null
}
```

### 2. 5G网络防御策略计算

**接口地址**: `/game/5g_strategy`

**支持方法**: `GET`, `POST`

**参数说明**:
- `budget`: 攻击者预算 (数值类型，非负)

**请求示例**:

GET请求:
```
GET /game/5g_strategy?budget=10000
```

POST请求:
```json
POST /game/5g_strategy
Content-Type: application/json

{
    "budget": 10000
}
```

**响应格式**:

成功响应 (200):
```json
{
    "status": "success",
    "data": {
        "reduce": 12.3,
        "game_cost": 8770.0,
        "single_cost": 10000.0,
        "budget": 10000,
        "atrategy1": 7645,
        "atrategy2": 9011,
        "atrategy3": 9754,
        "images": {
            "strategy1": "base64编码的策略1饼图",
            "strategy2": "base64编码的策略2饼图",
            "strategy3": "base64编码的策略3饼图",
            "attacker": "base64编码的攻击策略饼图",
            "effect": "base64编码的效果对比柱状图"
        }
    }
}
```

### 3. 卫星网络防御策略计算

**接口地址**: `/game/satellite_strategy`

**支持方法**: `GET`, `POST`

**参数说明**: 无需参数

**请求示例**:

GET请求:
```
GET /game/satellite_strategy
```

POST请求:
```json
POST /game/satellite_strategy
Content-Type: application/json

{}
```

**响应格式**:

成功响应 (200):
```json
{
    "status": "success",
    "data": {
        "reduce": 18.7,
        "game_cost": 8130.0,
        "single_cost": 10000.0,
        "images": {
            "strategy1": "base64编码的策略1饼图",
            "strategy2": "base64编码的策略2饼图",
            "strategy3": "base64编码的策略3饼图",
            "effect": "base64编码的效果对比柱状图"
        }
    }
}
```

### 4. 健康检查接口

**接口地址**: `/game/health`

**支持方法**: `GET`

**参数说明**: 无需参数

**响应格式**:
```json
{
    "status": "healthy",
    "service": "game_ability",
    "message": "博弈论防御策略计算服务运行正常",
    "endpoints": {
        "ip_strategy": "/game/ip_strategy",
        "5g_strategy": "/game/5g_strategy",
        "satellite_strategy": "/game/satellite_strategy"
    }
}
```

### 5. 服务信息接口

**接口地址**: `/game/info`

**支持方法**: `GET`

**参数说明**: 无需参数

**响应格式**: 返回详细的API使用说明和示例

## 错误处理

所有接口都采用统一的错误处理机制：

- **400 Bad Request**: 参数错误、验证失败
- **500 Internal Server Error**: 服务器内部错误

错误响应格式:
```json
{
    "error": "具体错误信息",
    "data": null
}
```

## 数据字段说明

### 响应数据字段

- `reduce`: 成本降低百分比 (相对于独立防御)
- `game_cost`: 博弈防御策略的总成本
- `single_cost`: 独立防御策略的总成本
- `images`: 包含各种策略图表的base64编码图片
  - `strategy1/2/3`: 各节点的防御策略分配饼图
  - `attacker`: 攻击策略分配饼图 (仅5G网络)
  - `effect`: 防御效果对比柱状图

### 图片说明

所有图片都以PNG格式生成，并转换为base64编码字符串。可以直接在前端使用：

```html
<img src="data:image/png;base64,{base64_string}" alt="策略图表" />
```

## 使用注意事项

1. **参数验证**: 所有数值参数必须为非负数
2. **请求格式**: POST请求必须使用JSON格式
3. **响应处理**: 建议检查响应中的`status`字段确认操作是否成功
4. **图片处理**: base64图片数据较大，建议按需加载
5. **错误处理**: 建议实现适当的错误处理和重试机制

## 集成示例

### Python客户端示例

```python
import requests
import json

# IP策略计算
response = requests.post('http://localhost:5000/game/ip_strategy', 
                        json={'input1': 1000, 'input2': 1500, 'input3': 2000})

if response.status_code == 200:
    result = response.json()
    if result['status'] == 'success':
        print(f"成本降低: {result['data']['reduce']}%")
        # 处理图片数据
        strategy1_img = result['data']['images']['strategy1']
    else:
        print(f"计算失败: {result.get('message', '未知错误')}")
else:
    print(f"请求失败: {response.status_code}")
```

### JavaScript客户端示例

```javascript
// 5G策略计算
fetch('/game/5g_strategy', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({budget: 10000})
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log(`成本降低: ${data.data.reduce}%`);
        // 显示图片
        document.getElementById('strategy1').src = 
            `data:image/png;base64,${data.data.images.strategy1}`;
    } else {
        console.error('计算失败:', data.error);
    }
})
.catch(error => console.error('请求错误:', error));
```
