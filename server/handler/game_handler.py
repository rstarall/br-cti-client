from flask import jsonify, request, Blueprint  # 导入Flask相关模块
import logging
import os
import sys

# 添加ability路径到系统路径，以便导入game_ability模块
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ability', 'game_ability'))

from ability.game_ability.game_ability import GameAbility  # 博弈论防御策略计算服务接口


# 创建博弈论防御策略蓝图
game_blue = Blueprint('game', __name__, url_prefix='/game')

# 实例化博弈论防御策略服务
game_service = GameAbility()


def validate_numeric_params(params, required_fields):
    """
    验证数值参数的有效性
    :param params: 参数字典
    :param required_fields: 必需字段列表
    :return: (is_valid, error_message)
    """
    for field in required_fields:
        if field not in params:
            return False, f"缺少必需参数: {field}"

        try:
            # 尝试转换为数值类型
            value = float(params[field])
            if value < 0:
                return False, f"参数 {field} 必须为非负数"
            params[field] = value
        except (ValueError, TypeError):
            return False, f"参数 {field} 必须为有效数值"

    return True, None


@game_blue.route('/ip_strategy', methods=['GET', 'POST'])
def ip_strategy():
    """
    IP网络防御策略计算接口

    支持GET和POST两种请求方式：
    - GET: 通过URL参数传递 input1, input2, input3
    - POST: 通过JSON body传递参数

    参数说明:
    - input1: 对节点1的攻击流量 (数值类型，非负)
    - input2: 对节点2的攻击流量 (数值类型，非负)
    - input3: 对节点3的攻击流量 (数值类型，非负)

    返回格式:
    成功: {
        "status": "success",
        "data": {
            "reduce": 成本降低百分比,
            "game_cost": 博弈防御成本,
            "single_cost": 独立防御成本,
            "input1": 输入参数1,
            "input2": 输入参数2,
            "input3": 输入参数3,
            "images": {
                "strategy1": 策略1饼图base64,
                "strategy2": 策略2饼图base64,
                "strategy3": 策略3饼图base64,
                "effect": 效果对比柱状图base64
            }
        }
    }
    失败: {"error": "错误信息", "data": None}
    """
    try:
        # 根据请求方法获取参数
        if request.method == 'GET':
            params = {
                'input1': request.args.get('input1'),
                'input2': request.args.get('input2'),
                'input3': request.args.get('input3')
            }
        else:  # POST
            if not request.is_json:
                return jsonify({'error': '请求必须为JSON格式', 'data': None}), 400
            params = request.get_json()
            if not params:
                return jsonify({'error': '请求体不能为空', 'data': None}), 400

        # 验证必需参数
        required_fields = ['input1', 'input2', 'input3']
        is_valid, error_msg = validate_numeric_params(params, required_fields)
        if not is_valid:
            return jsonify({'error': error_msg, 'data': None}), 400

        # 调用博弈论防御策略计算服务
        result = game_service.calculate_ip_strategy(
            params['input1'],
            params['input2'],
            params['input3']
        )

        # 检查计算结果
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            error_msg = result.get('message', '计算IP防御策略失败')
            return jsonify({'error': error_msg, 'data': None}), 400

    except Exception as e:
        logging.error(f"IP策略计算接口异常: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}', 'data': None}), 500


@game_blue.route('/5g_strategy', methods=['GET', 'POST'])
def fiveg_strategy():
    """
    5G网络防御策略计算接口

    支持GET和POST两种请求方式：
    - GET: 通过URL参数传递 budget
    - POST: 通过JSON body传递参数

    参数说明:
    - budget: 攻击者预算 (数值类型，非负)

    返回格式:
    成功: {
        "status": "success",
        "data": {
            "reduce": 成本降低百分比,
            "game_cost": 博弈防御成本,
            "single_cost": 独立防御成本,
            "budget": 攻击者预算,
            "atrategy1": 攻击策略1,
            "atrategy2": 攻击策略2,
            "atrategy3": 攻击策略3,
            "images": {
                "strategy1": 策略1饼图base64,
                "strategy2": 策略2饼图base64,
                "strategy3": 策略3饼图base64,
                "attacker": 攻击策略饼图base64,
                "effect": 效果对比柱状图base64
            }
        }
    }
    失败: {"error": "错误信息", "data": None}
    """
    try:
        # 根据请求方法获取参数
        if request.method == 'GET':
            params = {
                'budget': request.args.get('budget')
            }
        else:  # POST
            if not request.is_json:
                return jsonify({'error': '请求必须为JSON格式', 'data': None}), 400
            params = request.get_json()
            if not params:
                return jsonify({'error': '请求体不能为空', 'data': None}), 400

        # 验证必需参数
        required_fields = ['budget']
        is_valid, error_msg = validate_numeric_params(params, required_fields)
        if not is_valid:
            return jsonify({'error': error_msg, 'data': None}), 400

        # 调用博弈论防御策略计算服务
        result = game_service.calculate_5g_strategy(params['budget'])

        # 检查计算结果
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            error_msg = result.get('message', '计算5G防御策略失败')
            return jsonify({'error': error_msg, 'data': None}), 400

    except Exception as e:
        logging.error(f"5G策略计算接口异常: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}', 'data': None}), 500


@game_blue.route('/satellite_strategy', methods=['GET', 'POST'])
def satellite_strategy():
    """
    卫星网络防御策略计算接口

    支持GET和POST两种请求方式，无需参数

    返回格式:
    成功: {
        "status": "success",
        "data": {
            "reduce": 成本降低百分比,
            "game_cost": 博弈防御成本,
            "single_cost": 独立防御成本,
            "images": {
                "strategy1": 策略1饼图base64,
                "strategy2": 策略2饼图base64,
                "strategy3": 策略3饼图base64,
                "effect": 效果对比柱状图base64
            }
        }
    }
    失败: {"error": "错误信息", "data": None}
    """
    try:
        # 调用博弈论防御策略计算服务
        result = game_service.calculate_satellite_strategy()

        # 检查计算结果
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            error_msg = result.get('message', '计算卫星防御策略失败')
            return jsonify({'error': error_msg, 'data': None}), 400

    except Exception as e:
        logging.error(f"卫星策略计算接口异常: {str(e)}")
        return jsonify({'error': f'服务器内部错误: {str(e)}', 'data': None}), 500


@game_blue.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口

    返回服务状态信息
    """
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'game_ability',
            'message': '博弈论防御策略计算服务运行正常',
            'endpoints': {
                'ip_strategy': '/game/ip_strategy',
                '5g_strategy': '/game/5g_strategy',
                'satellite_strategy': '/game/satellite_strategy'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@game_blue.route('/info', methods=['GET'])
def service_info():
    """
    服务信息接口

    返回详细的API使用说明
    """
    return jsonify({
        'service_name': '博弈论防御策略计算服务',
        'version': '1.0.0',
        'description': '提供IP网络、5G网络和卫星网络的博弈论防御策略计算功能',
        'endpoints': {
            '/game/ip_strategy': {
                'methods': ['GET', 'POST'],
                'description': 'IP网络防御策略计算',
                'parameters': {
                    'input1': '对节点1的攻击流量 (数值，非负)',
                    'input2': '对节点2的攻击流量 (数值，非负)',
                    'input3': '对节点3的攻击流量 (数值，非负)'
                },
                'example_get': '/game/ip_strategy?input1=1000&input2=1500&input3=2000',
                'example_post': {
                    'url': '/game/ip_strategy',
                    'body': {'input1': 1000, 'input2': 1500, 'input3': 2000}
                }
            },
            '/game/5g_strategy': {
                'methods': ['GET', 'POST'],
                'description': '5G网络防御策略计算',
                'parameters': {
                    'budget': '攻击者预算 (数值，非负)'
                },
                'example_get': '/game/5g_strategy?budget=10000',
                'example_post': {
                    'url': '/game/5g_strategy',
                    'body': {'budget': 10000}
                }
            },
            '/game/satellite_strategy': {
                'methods': ['GET', 'POST'],
                'description': '卫星网络防御策略计算',
                'parameters': '无需参数',
                'example_get': '/game/satellite_strategy',
                'example_post': {
                    'url': '/game/satellite_strategy',
                    'body': {}
                }
            },
            '/game/health': {
                'methods': ['GET'],
                'description': '健康检查接口'
            },
            '/game/info': {
                'methods': ['GET'],
                'description': '服务信息接口'
            }
        },
        'response_format': {
            'success': {
                'status': 'success',
                'data': {
                    'reduce': '成本降低百分比',
                    'game_cost': '博弈防御成本',
                    'single_cost': '独立防御成本',
                    'images': {
                        'strategy1': '策略1图片base64编码',
                        'strategy2': '策略2图片base64编码',
                        'strategy3': '策略3图片base64编码',
                        'effect': '效果对比图片base64编码'
                    }
                }
            },
            'error': {
                'error': '错误信息',
                'data': None
            }
        }
    }), 200