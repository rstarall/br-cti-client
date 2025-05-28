from flask import Flask, request, jsonify
from game_ability import GameAbility

# 初始化Flask应用
app = Flask(__name__)
game_ability = GameAbility()

# 健康检查接口
@app.route('/')
def health_check():
    return jsonify({
        "status": "success",
        "message": "Game Ability API is running",
        "version": "1.0.0",
        "endpoints": [
            "/api/ip",
            "/api/5g",
            "/api/satellite",
            "/api/strategy"
        ]
    })

# IP网络策略计算接口
@app.route('/api/ip', methods=['POST'])
def calculate_ip():
    """
    IP网络防御策略计算接口
    接收参数: input1, input2, input3 (对各节点的攻击流量)
    返回: 包含策略数据和图片base64的JSON
    """
    try:
        data = request.get_json()
        input1 = int(data.get('input1', 0))
        input2 = int(data.get('input2', 0))
        input3 = int(data.get('input3', 0))

        result = game_ability.calculate_ip_strategy(input1, input2, input3)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"IP策略计算错误: {str(e)}"
        }), 400

# 5G网络策略计算接口
@app.route('/api/5g', methods=['POST'])
def calculate_5g():
    """
    5G网络防御策略计算接口
    接收参数: budget (攻击者预算)
    返回: 包含策略数据和图片base64的JSON
    """
    try:
        data = request.get_json()
        budget = int(data.get('budget', 0))

        result = game_ability.calculate_5g_strategy(budget)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"5G策略计算错误: {str(e)}"
        }), 400

# 卫星网络策略计算接口
@app.route('/api/satellite', methods=['POST'])
def calculate_satellite():
    """
    卫星网络防御策略计算接口
    无需参数，使用预设参数计算
    返回: 包含策略数据和图片base64的JSON
    """
    try:
        result = game_ability.calculate_satellite_strategy()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"卫星策略计算错误: {str(e)}"
        }), 400

# 通用策略计算接口
@app.route('/api/strategy', methods=['POST'])
def calculate_strategy():
    """
    通用策略计算接口
    接收参数:
    - strategy_type: "ip", "5g", "satellite"
    - 其他参数根据策略类型而定
    返回: 包含策略数据和图片base64的JSON
    """
    try:
        data = request.get_json()
        strategy_type = data.get('strategy_type', '').lower()

        if strategy_type == 'ip':
            input1 = int(data.get('input1', 0))
            input2 = int(data.get('input2', 0))
            input3 = int(data.get('input3', 0))
            result = game_ability.calculate_ip_strategy(input1, input2, input3)
        elif strategy_type == '5g':
            budget = int(data.get('budget', 0))
            result = game_ability.calculate_5g_strategy(budget)
        elif strategy_type == 'satellite':
            result = game_ability.calculate_satellite_strategy()
        else:
            return jsonify({
                "status": "error",
                "message": "不支持的策略类型，支持的类型: ip, 5g, satellite"
            }), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"策略计算错误: {str(e)}"
        }), 400



if __name__ == '__main__':
    app.run(debug=True, port=5006)  # 启动Flask开发服务器，端口5006
