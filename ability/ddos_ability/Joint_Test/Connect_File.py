import json
from datetime import datetime

current_date = datetime.now()

# 格式化日期为 "YYYY-MM-DD"
formatted_date = current_date.strftime("%Y-%m-%d")

def read_file(file_path):
    try:
        # 打开并读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # 解析 JSON 数据
        # 打印 JSON 数据
        print("JSON 文件内容:")
        print(json.dumps(data, indent=4))  # 格式化输出

    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"错误: 文件 {file_path} 不是有效的 JSON 格式。")
    except Exception as e:
        print(f"发生未知错误: {e}")
    return data


def read_portMappings():
    path = '/data/portList/'
    # portMappings_2025-02-09.json
    # 获取当前日期
    return read_file(path+'PortMappings_'+formatted_date+'.json')


def read_ipMappings():
    path = '/data/ipList/'
    return read_file(path+'PortMappings_'+formatted_date+'.json')


def read_domainMappings():
    path = '/data/domainList/'
    return read_file(path + 'domainMappings_'+formatted_date + '.json')

def read_domainDetailsMapings():
    path = '/data/domainDetailList/'
    return read_file(path + 'domainDetailsMappings_' +formatted_date + '.json')