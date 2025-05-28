import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ability', 'game_ability'))

from game_ability import GameAbility
import json

def test_game_ability():
    """测试GameAbility类的各个功能"""
    print("开始测试GameAbility类...")

    # 创建GameAbility实例
    game_ability = GameAbility()
    print("✓ GameAbility实例创建成功")

    # 测试IP策略计算
    print("\n测试IP策略计算...")
    try:
        result = game_ability.calculate_ip_strategy(15000, 20000, 25000)
        print(f"✓ IP策略计算成功")
        print(f"  状态: {result['status']}")
        if result['status'] == 'success':
            data = result['data']
            print(f"  成本降低: {data['reduce']:.2f}%")
            print(f"  博弈成本: {data['game_cost']}")
            print(f"  独立成本: {data['single_cost']}")
            print(f"  图片数量: {len(data['images'])}")
            # 验证base64图片
            for img_name, img_data in data['images'].items():
                if img_data.startswith('iVBORw0KGgo'):  # PNG base64开头
                    print(f"  ✓ {img_name}图片生成成功")
                else:
                    print(f"  ✗ {img_name}图片格式错误")
    except Exception as e:
        print(f"✗ IP策略计算失败: {e}")

    # 测试5G策略计算
    print("\n测试5G策略计算...")
    try:
        result = game_ability.calculate_5g_strategy(135000)
        print(f"✓ 5G策略计算成功")
        print(f"  状态: {result['status']}")
        if result['status'] == 'error':
            print(f"  错误信息: {result.get('message', '未知错误')}")
        if result['status'] == 'success':
            data = result['data']
            print(f"  成本降低: {data['reduce']:.2f}%")
            print(f"  博弈成本: {data['game_cost']}")
            print(f"  独立成本: {data['single_cost']}")
            print(f"  攻击策略1: {data['atrategy1']}")
            print(f"  攻击策略2: {data['atrategy2']}")
            print(f"  攻击策略3: {data['atrategy3']}")
            print(f"  图片数量: {len(data['images'])}")
            # 验证base64图片
            for img_name, img_data in data['images'].items():
                if img_data.startswith('iVBORw0KGgo'):  # PNG base64开头
                    print(f"  ✓ {img_name}图片生成成功")
                else:
                    print(f"  ✗ {img_name}图片格式错误")
    except Exception as e:
        print(f"✗ 5G策略计算失败: {e}")

    # 测试卫星策略计算
    print("\n测试卫星策略计算...")
    try:
        result = game_ability.calculate_satellite_strategy()
        print(f"✓ 卫星策略计算成功")
        print(f"  状态: {result['status']}")
        if result['status'] == 'success':
            data = result['data']
            print(f"  成本降低: {data['reduce']:.2f}%")
            print(f"  博弈成本: {data['game_cost']}")
            print(f"  独立成本: {data['single_cost']}")
            print(f"  图片数量: {len(data['images'])}")
            # 验证base64图片
            for img_name, img_data in data['images'].items():
                if img_data.startswith('iVBORw0KGgo'):  # PNG base64开头
                    print(f"  ✓ {img_name}图片生成成功")
                else:
                    print(f"  ✗ {img_name}图片格式错误")
    except Exception as e:
        print(f"✗ 卫星策略计算失败: {e}")

    print("\n测试完成！")

def test_api_format():
    """测试API返回格式是否符合预期"""
    print("\n测试API返回格式...")

    game_ability = GameAbility()

    # 测试IP策略返回格式
    result = game_ability.calculate_ip_strategy(10000, 15000, 20000)

    expected_keys = ['status', 'data']
    if result['status'] == 'success':
        expected_data_keys = ['reduce', 'game_cost', 'single_cost', 'input1', 'input2', 'input3', 'images']
        expected_image_keys = ['strategy1', 'strategy2', 'strategy3', 'effect']

        # 检查顶级键
        for key in expected_keys:
            if key in result:
                print(f"  ✓ 包含键: {key}")
            else:
                print(f"  ✗ 缺少键: {key}")

        # 检查data键
        if 'data' in result:
            for key in expected_data_keys:
                if key in result['data']:
                    print(f"  ✓ data包含键: {key}")
                else:
                    print(f"  ✗ data缺少键: {key}")

            # 检查images键
            if 'images' in result['data']:
                for key in expected_image_keys:
                    if key in result['data']['images']:
                        print(f"  ✓ images包含键: {key}")
                    else:
                        print(f"  ✗ images缺少键: {key}")

if __name__ == "__main__":
    test_game_ability()
    test_api_format()
