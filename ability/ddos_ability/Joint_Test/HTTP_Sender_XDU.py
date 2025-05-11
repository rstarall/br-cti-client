import json
from HTTP_Sender import HTTP_Client  # 假设HTTP_Client是一个发送HTTP请求的类或函数
import argparse
from Connect_DB import *
from Connect_Suricata import *
from Connect_File import *
import argparse

# 服务端IP地址和端口号
SERVER_IP = "10.2.87.80"
SERVER_PORT = 9998
# 基础URL路径（不包括动作部分）
BASE_URL_PATH = "/api"


def main():
    parser = argparse.ArgumentParser(description="choices")
    parser.add_argument("action", choices=[
        "ip_period", "port_period", "node_period", "network_topology",
        "ipMappings", "portMappings", "domainMappings", "domainDetailsMappings",
        "dos_alert", "penetration_alert", "scan_alert"
    ], help="选择传输哪些数据")

    args = parser.parse_args()

    # 根据action构建完整的URL路径
    url_path = f"{BASE_URL_PATH}/{args.action}"
    url = f"http://{SERVER_IP}:{SERVER_PORT}{url_path}"

    # 根据action获取相应的数据或发送警报
    if args.action == "ip_period":
        data = ip_period_select()
    elif args.action == "port_period":
        data = port_period_select()
    elif args.action == "node_period":
        data = node_period_select()
    elif args.action == "network_topology":
        data = network_topology_select()
    elif args.action == "ipMappings":
        data = read_ipMappings()
    elif args.action == "portMappings":
        data = read_portMappings()
    elif args.action == "domainMappings":
        data = read_domainMappings()
    elif args.action == "domainDetailsMappings":
        data =  read_domainDetailsMapings()
    elif args.action == "dos_alert":
        # 假设Send_Alert_TO_XJTU在发送警报时不返回数据，只发送请求
        response = Send_Alert_TO_XJTU("dos")  # 注意：这里可能需要根据实际函数参数调整
        # 由于不返回数据，我们可以不设置data变量，或者设置为None以表示没有数据要发送
        data = None  # 如果HTTP_Client需要data参数，并且对于警报可以设置为空字典或其他适当值
    elif args.action == "penetration_alert":
        response = Send_Alert_TO_XJTU("penetration")  # 同上
        data = None  # 或其他适当值
    elif args.action == "scan_alert":
        response = Send_Alert_TO_XJTU("scan")  # 同上
        data = None  # 或其他适当值

    # 如果data不是None，则使用HTTP客户端发送数据
    if data is not None:
        HTTP_Client(url, data)  # 注意：确保HTTP_Client能够处理字典类型的data

if __name__ == "__main__":
    main()