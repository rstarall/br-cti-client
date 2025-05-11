import socket
import json


#发送端
def UDP_Client(ip:str, port:int, data:str):
    #创建udp套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #定义服务器地址和端口
    server_address = (ip, port)
    #要发送的json数据
    json_data = data
    print(json_data)
    client_socket.sendto(json_data.encode('utf-8'), server_address)
    print(client_socket.recv(1024).decode('utf-8'))
    # print("数据已发送")
    client_socket.close()

if __name__ == "__main__":
    #要发送的json数据
    data = {
      "sid_rev":"active_defense_subsystem",
      "src": "10.2.87.12", #源IP
      "dst": "10.10.128.23", # 目标IP
      "alarm": "dos",#告警内容
      "level": "2", # 风险等级:1,2,3.
      "timestamp":"2024-5-18 15:12:18", #发现时间
      "defense_id": ["active_defense_subsyste_01"],# 01: 端口跳变，02：IP跳变，03：流量牵引
      "other": {
        "rule": "TCP", #协议
      }
    }
    #服务端IP
    IP = "127.0.0.1"
    #服务端端口号
    PORT = 9998
    UDP_Client(IP, PORT, json.dumps(data))