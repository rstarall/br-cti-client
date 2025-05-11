import re
# from UDP_Sender import *
import json
from datetime import datetime

current_date = datetime.now()
# 格式化日期为 "YYYY-MM-DD"
formatted_date = current_date.strftime("%Y-%m-%d")

#1、Dos攻击告警数据格式
dos_alert = {
  "timestamp":"2024-5-18 15:12:18", #发现时间
  "sid_rev":"active_defense_subsystem",
  "src": "10.2.87.12", #//源IP
  "dst": "10.10.128.23", #// 目标IP
  "alarm": "dos",#//告警内容
  "defense_id": ["active_defense_subsystem_03"],#// 01: 端口跳变，02：IP跳变，03：流量牵引
    "level": "2", #// 风险等级:1,2,3.
  "other": {
    "time": "2024-5-18 15:12:18" #// dos攻击发生时间
    }
}
# 2、扫描攻击告警数据格式
scan_alert = {
  "timestamp":"2024-5-18 15:12:18",# //发现时间
  "sid_rev":"active_defense_subsystem",
  "src": "10.2.87.12",# //源IP
  "dst": "10.10.128.23",# // 目标IP
  "alarm": "扫描攻击",#//告警内容
  "defense_id": ["active_defense_subsystem_01"],
  "level": "2",# // 风险等级:1,2,3.
   "other": {
    "time": "2024-5-18 15:12:18" #// 扫描攻击发生时间
}
}
#3、渗透提权告警数据格式
penetration_alert = {
  "timestamp":"2024-5-18 15:12:18", # //发现时间
  "sid_rev":"active_defense_subsystem",
  "src": "10.2.87.12", # //源IP
  "dst": "10.10.128.23", # // 目标IP
  "alarm": "渗透提权", #//告警内容
  "defense_id": ["active_defense_subsystem_03"], #// 01: 端口跳变，02：IP跳变，03：流量牵引
  "level": "2", #// 风险等级:1,2,3.
  "other": {
    "time": "2024-5-18 15:12:18"# // 渗透提权发生时间
  }
}

alert_path = '/var/log/suricata/eve.json'
import os
def Send_Alert_TO_XJTU(alert_type):
    print(alert_path)
    if not os.path.exists(alert_path):
        print(f"错误: 文件 {alert_path} 不存在。")

    dos_alert_list = []
    scan_alert_list = []
    penetration_alert_list = []

    with open(alert_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = json.loads(line.strip())

            if 'alert' in line and 'signature' in line['alert']:
                # 解析为 datetime 对象
                corrected_timestamp_str = line["timestamp"].replace("+0800", "+08:00")
                dt = datetime.fromisoformat(corrected_timestamp_str)
                # 格式化为 "YYYY-MM-DD"
                alert_formatted_date = dt.strftime("%Y-%m-%d")
                if alert_formatted_date == formatted_date:
                    if re.search('Dos', line["alert"]["signature"], re.IGNORECASE):
                        dos_alert["timestamp"] = line["timestamp"]
                        dos_alert["src"] = line["src_ip"]
                        dos_alert["dst"] = line["dest_ip"]
                        dos_alert["other"]["time"] = line["timestamp"]
                        dos_alert_list.append(dos_alert)

                    # if line["alert"]["signature"] in ['渗透提权']:
                    if re.search('渗透提权', line["alert"]["signature"], re.IGNORECASE):
                        scan_alert["timestamp"] = line["timestamp"]
                        scan_alert["src"] = line["src_ip"]
                        scan_alert["dst"] = line["dest_ip"]
                        scan_alert["other"]["time"] = line["timestamp"]

                        scan_alert_list.append(scan_alert)

                    # if line["alert"]["signature"] in ['扫描']:
                    if re.search('扫描', line["alert"]["signature"], re.IGNORECASE):
                        penetration_alert["timestamp"] = line["timestamp"]
                        penetration_alert["src"] = line["src_ip"]
                        penetration_alert["dst"] = line["dest_ip"]
                        penetration_alert["other"]["time"] = line["timestamp"]
                        if formatted_date == current_date:
                            penetration_alert_list.append(penetration_alert)

    if alert_type=='penetration_alert':
        return penetration_alert_list
    elif alert_type=='dos_alert':
        return dos_alert_list
    elif alert_type=='scan_alert':
        return scan_alert_list


# Send_Alert_TO_XJTU('penetration_alert')

#
# def receive_from_XJTU():
#     IP = "10.2.88.19"
#     # # 服务端端口号
#     PORT = 9998
#     with open(path, 'r', encoding='utf-8') as file:
#         for line in file:
#             # print(line.strip())  # 去除每行末尾的换行符
#             line = json.loads(line.strip())
#             # if line["alert"]["signature"] in ['Dos','dos']:
#             if re.search('Dos', line["alert"]["signature"], re.IGNORECASE):
#                 dos_alert["timestamp"] = line["timestamp"]
#                 dos_alert["src"] = line["src_ip"]
#                 dos_alert["dst"] = line["dest_ip"]
#                 dos_alert["other"]["time"] = line["timestamp"]
#
#                 UDP_Client(IP, PORT, json.dumps(dos_alert))
#
#             # if line["alert"]["signature"] in ['渗透提权']:
#             if re.search('渗透提权', line["alert"]["signature"], re.IGNORECASE):
#                 scan_alert["timestamp"] = line["timestamp"]
#                 scan_alert["src"] = line["src_ip"]
#                 scan_alert["dst"] = line["dest_ip"]
#                 scan_alert["other"]["time"] = line["timestamp"]
#
#                 UDP_Client(IP, PORT, json.dumps(scan_alert))
#
#             # if line["alert"]["signature"] in ['扫描']:
#             if re.search('扫描', line["alert"]["signature"], re.IGNORECASE):
#                 penetration_alert["timestamp"] = line["timestamp"]
#                 penetration_alert["src"] = line["src_ip"]
#                 penetration_alert["dst"] = line["dest_ip"]
#                 penetration_alert["other"]["time"] = line["timestamp"]
#
#                 UDP_Client(IP, PORT, json.dumps(penetration_alert))


# # 访问 JSON 中的具体字段
# if isinstance(data, dict):  # 确保 JSON 是字典类型
#     print(data.get('key'))  # 获取指定键的值


# decoder = json.JSONDecoder()

# with open(path, 'r') as file:
#     content = file.read()
#     pos = 0
#     while pos < len(content):
#         try:
#             obj, pos = decoder.raw_decode(content, pos)
#             print(obj)  # 处理解析后的 JSON 对象
#         except json.JSONDecodeError as e:
#             print(f"JSONDecodeError: {e}")
#             break