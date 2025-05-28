#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博弈论防御策略计算服务测试脚本

测试 server/handler/game_handler.py 的各个接口功能
"""

import sys
import os
import requests
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_game_handler_import():
    """测试game_handler模块导入"""
    try:
        from server.handler.game_handler import game_blue, game_service
        print("✅ game_handler模块导入成功")
        print(f"   - 蓝图名称: {game_blue.name}")
        print(f"   - URL前缀: {game_blue.url_prefix}")
        print(f"   - 服务实例: {type(game_service).__name__}")
        return True
    except Exception as e:
        print(f"❌ game_handler模块导入失败: {e}")
        return False

def test_game_ability_import():
    """测试GameAbility类导入和实例化"""
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ability', 'game_ability'))
        from ability.game_ability.game_ability import GameAbility
        
        service = GameAbility()
        print("✅ GameAbility类导入和实例化成功")
        print(f"   - 类名: {type(service).__name__}")
        
        # 测试方法是否存在
        methods = ['calculate_ip_strategy', 'calculate_5g_strategy', 'calculate_satellite_strategy']
        for method in methods:
            if hasattr(service, method):
                print(f" - 方法 {method}: 存在")
            else:
                print(f" - 方法 {method}: 不存在")
        
        return True
    except Exception as e:
        print(f"❌ GameAbility类导入失败: {e}")
        return False

def test_ip_strategy_calculation():
    """测试IP策略计算功能"""
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ability', 'game_ability'))
        from ability.game_ability.game_ability import GameAbility
        
        service = GameAbility()
        
        # 测试参数
        input1, input2, input3 = 1000, 1500, 2000
        
        print(f"🧪 测试IP策略计算 (input1={input1}, input2={input2}, input3={input3})")
        
        result = service.calculate_ip_strategy(input1, input2, input3)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print("✅ IP策略计算成功")
            print(f"   - 成本降低: {data.get('reduce', 'N/A')}%")
            print(f"   - 博弈防御成本: {data.get('game_cost', 'N/A')}")
            print(f"   - 独立防御成本: {data.get('single_cost', 'N/A')}")
            print(f"   - 图片数量: {len(data.get('images', {}))}")
            return True
        else:
            print(f"❌ IP策略计算失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ IP策略计算测试异常: {e}")
        return False

def test_5g_strategy_calculation():
    """测试5G策略计算功能"""
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ability', 'game_ability'))
        from ability.game_ability.game_ability import GameAbility
        
        service = GameAbility()
        
        # 测试参数
        budget = 10000
        
        print(f"🧪 测试5G策略计算 (budget={budget})")
        
        result = service.calculate_5g_strategy(budget)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print("✅ 5G策略计算成功")
            print(f"   - 成本降低: {data.get('reduce', 'N/A')}%")
            print(f"   - 博弈防御成本: {data.get('game_cost', 'N/A')}")
            print(f"   - 独立防御成本: {data.get('single_cost', 'N/A')}")
            print(f"   - 图片数量: {len(data.get('images', {}))}")
            return True
        else:
            print(f"❌ 5G策略计算失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 5G策略计算测试异常: {e}")
        return False

def test_satellite_strategy_calculation():
    """测试卫星策略计算功能"""
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ability', 'game_ability'))
        from ability.game_ability.game_ability import GameAbility
        
        service = GameAbility()
        
        print("🧪 测试卫星策略计算")
        
        result = service.calculate_satellite_strategy()
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print("✅ 卫星策略计算成功")
            print(f"   - 成本降低: {data.get('reduce', 'N/A')}%")
            print(f"   - 博弈防御成本: {data.get('game_cost', 'N/A')}")
            print(f"   - 独立防御成本: {data.get('single_cost', 'N/A')}")
            print(f"   - 图片数量: {len(data.get('images', {}))}")
            return True
        else:
            print(f"❌ 卫星策略计算失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 卫星策略计算测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("博弈论防御策略计算服务测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_game_handler_import),
        ("GameAbility类测试", test_game_ability_import),
        ("IP策略计算测试", test_ip_strategy_calculation),
        ("5G策略计算测试", test_5g_strategy_calculation),
        ("卫星策略计算测试", test_satellite_strategy_calculation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"   测试失败")
        except Exception as e:
            print(f"   测试异常: {e}")
        
        time.sleep(0.5)  # 短暂延迟
    
    print("\n" + "=" * 60)
    print(f"测试总结: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
