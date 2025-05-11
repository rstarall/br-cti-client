import json
from UDP_Sender import *
from Connect_DB import *
from Connect_Suricata import *
from Connect_File import *
import argparse

IP = "10.2.87.80"
# 服务端端口号
PORT = 9998

parser = argparse.ArgumentParser(description="choices")
parser.add_argument("action", choices=["ip_period", "port_period", "node_period","network_topology",
                                       "ipMappings","portMappings","domainMappings","domainDetailsMappings",
                                       "dos_alert","penetration_alert","scan_alert"
                                       ], help="选择传输哪些数据")
# parser.add_argument("--name", type=str, default="default_name", help="指定名称")

args = parser.parse_args()

if args.action == "ip_period":
    ip_period = ip_period_select()
    UDP_Client(IP, PORT, json.dumps(ip_period))

if args.action == "port_period":
    port_period = port_period_select()
    UDP_Client(IP, PORT, json.dumps(port_period))

if args.action == "node_period":
    node_period = node_period_select()
    UDP_Client(IP, PORT, json.dumps(node_period))

if args.action == "network_topology":
    network_topology = network_topology_select()
    UDP_Client(IP, PORT, json.dumps(network_topology))

if args.action == "ipMappings":
    ipMappings = read_ipMappings()
    UDP_Client(IP, PORT, json.dumps(ipMappings))

if args.action == "portMappings":
    portMappings = read_portMappings()
    UDP_Client(IP, PORT, json.dumps(portMappings))

if args.action == 'domainMappings':
    domainMappings = read_domainMappings()
    UDP_Client(IP, PORT, json.dumps(domainMappings))

if args.action == 'domainDetailsMappings':
    domainDetailsMappings = read_domainDetailsMapings()
    UDP_Client(IP, PORT, json.dumps(domainDetailsMappings))

if args.action == "dos_alert" or args.action =="penetration_alert" or args.action =="scan_alert":
    alert = Send_Alert_TO_XJTU(args.action)
    UDP_Client(IP, PORT, json.dumps(alert))
