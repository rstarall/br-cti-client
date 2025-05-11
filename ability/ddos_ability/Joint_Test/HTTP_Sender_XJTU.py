import json
import requests  # 确保导入了requests库
from HTTP_Sender import HTTP_Client 
from Connect_DB import *
from Connect_Suricata import *
from Connect_File import *
import argparse

# HTTP服务器URL
SERVER_URL = "http://10.2.88.19:9999/api"  # 请根据实际情况修改URL，包括端口号和路径

parser = argparse.ArgumentParser(description="choices")
parser.add_argument("--action", choices=[
    "ip_period", "port_period", "node_period", "network_topology",
    "ipMappings", "portMappings", "domainMappings", "domainDetailsMappings",
    "dos_alert", "penetration_alert", "scan_alert"
], help="选择传输哪些数据")

parser.add_argument("--data", default=None, help="要发送的数据")
args = parser.parse_args()


# 根据选择的action发送数据
if args.action == "ip_period":
    data_to_send = {
        'action': args.action,
        'ip_period': args.data
    }
    HTTP_Client(SERVER_URL, data_to_send)

elif args.action == "port_period":
    data_to_send = {
        'action': args.action,
        'port_period': args.data
    }
    HTTP_Client(SERVER_URL, data_to_send)

elif args.action == "node_period":
    data_to_send = {
        'action': args.action,
        'node_period': args.data
    }
    HTTP_Client(SERVER_URL, data_to_send)


