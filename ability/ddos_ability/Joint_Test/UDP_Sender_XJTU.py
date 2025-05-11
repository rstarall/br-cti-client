import json
from UDP_Sender import *
from Connect_DB import *
from Connect_Suricata import *
IP = "10.2.88.19"
# 服务端端口号
PORT = 9999

import json
from UDP_Sender import *
from Connect_DB import *
from Connect_Suricata import *
from Connect_File import *
import argparse


parser = argparse.ArgumentParser(description="choices")
parser.add_argument("--action", choices=["ip_period", "port_period", "node_period","network_topology",
                                       "ipMappings","portMappings","domainMappings","domainDetailsMappings",
                                       "dos_alert","penetration_alert","scan_alert"
                                       ], help="选择传输哪些数据")

parser.add_argument("--data",default=None, help="交大发的命令")
args = parser.parse_args()

if args.action == "ip_period":
    ip_period_dict ={
        'action': args.action,
        'ip_period': args.data
    }
    print(ip_period_dict)
    UDP_Client(IP, PORT, json.dumps(ip_period_dict))

if args.action == "port_period":
    port_period_dict = {
        'action': args.action,
        'port_period':args.data
    }
    UDP_Client(IP, PORT, json.dumps(port_period_dict))

if args.action == "node_period":
    node_period_dict = {
        'action': args.action,
        'node_period': args.data
    }
    UDP_Client(IP, PORT, json.dumps(node_period_dict))

if args.action == "traction_order":
    ip_period_dict = {
        'action': args.action,
        'traction_order': args.data
    }
    UDP_Client(IP, PORT, json.dumps(ip_period_dict))



