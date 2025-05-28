import requests
import json
import base64
import time

def test_api_endpoints():
    """测试Flask API端点"""
    base_url = "http://localhost:5006"
    
    print("开始测试Flask API端点...")
    print("注意：请确保Flask应用正在运行 (python ability/game_ability/app.py)")
    
    # 等待用户确认
    input("按Enter键继续测试...")
    
    # 测试IP策略API
    print("\n测试IP策略API...")
    try:
        response = requests.post(f"{base_url}/api/ip", 
                               json={"input1": 15000, "input2": 20000, "input3": 25000},
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ IP策略API调用成功")
            print(f"  状态: {result['status']}")
            if result['status'] == 'success':
                data = result['data']
                print(f"  成本降低: {data['reduce']:.2f}%")
                print(f"  图片数量: {len(data['images'])}")
                # 验证base64图片
                for img_name, img_data in data['images'].items():
                    if img_data and len(img_data) > 100:  # 简单验证
                        print(f"  ✓ {img_name}图片数据有效")
                    else:
                        print(f"  ✗ {img_name}图片数据无效")
        else:
            print(f"✗ IP策略API调用失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ IP策略API调用异常: {e}")
    
    # 测试5G策略API
    print("\n测试5G策略API...")
    try:
        response = requests.post(f"{base_url}/api/5g", 
                               json={"budget": 135000},
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 5G策略API调用成功")
            print(f"  状态: {result['status']}")
            if result['status'] == 'success':
                data = result['data']
                print(f"  成本降低: {data['reduce']:.2f}%")
                print(f"  图片数量: {len(data['images'])}")
        else:
            print(f"✗ 5G策略API调用失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 5G策略API调用异常: {e}")
    
    # 测试卫星策略API
    print("\n测试卫星策略API...")
    try:
        response = requests.post(f"{base_url}/api/satellite", 
                               json={},
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 卫星策略API调用成功")
            print(f"  状态: {result['status']}")
            if result['status'] == 'success':
                data = result['data']
                print(f"  成本降低: {data['reduce']:.2f}%")
                print(f"  图片数量: {len(data['images'])}")
        else:
            print(f"✗ 卫星策略API调用失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 卫星策略API调用异常: {e}")
    
    # 测试通用策略API
    print("\n测试通用策略API...")
    try:
        response = requests.post(f"{base_url}/api/strategy", 
                               json={"strategy_type": "ip", "input1": 10000, "input2": 15000, "input3": 20000},
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 通用策略API调用成功")
            print(f"  状态: {result['status']}")
        else:
            print(f"✗ 通用策略API调用失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ 通用策略API调用异常: {e}")
    
    print("\nAPI测试完成！")

def save_sample_images():
    """保存示例图片到文件"""
    print("\n保存示例图片...")
    
    # 导入GameAbility类
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ability', 'game_ability'))
    
    from game_ability import GameAbility
    
    game_ability = GameAbility()
    
    # 生成IP策略图片
    result = game_ability.calculate_ip_strategy(15000, 20000, 25000)
    if result['status'] == 'success':
        images = result['data']['images']
        for img_name, img_data in images.items():
            # 解码base64并保存为PNG文件
            img_bytes = base64.b64decode(img_data)
            filename = f"sample_ip_{img_name}.png"
            with open(filename, 'wb') as f:
                f.write(img_bytes)
            print(f"✓ 保存图片: {filename}")
    
    print("示例图片保存完成！")

if __name__ == "__main__":
    # 选择测试类型
    print("选择测试类型:")
    print("1. 测试API端点 (需要Flask应用运行)")
    print("2. 保存示例图片")
    choice = input("请输入选择 (1 或 2): ")
    
    if choice == "1":
        test_api_endpoints()
    elif choice == "2":
        save_sample_images()
    else:
        print("无效选择")
