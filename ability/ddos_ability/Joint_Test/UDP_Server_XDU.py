import socket
from Connect_DB import *
import json
def udp_server_write_to_db():
    """
    使用UDP的通信双方也分为客户端和服务器。
    服务器首先需要绑定端口：
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口:
    s.bind(('127.0.0.1', 9999))
    print('Bind UDP on 9999...')

    while True:
        # 接收数据:
        data, addr = s.recvfrom(1024)
        # recvfrom()方法返回数据和客户端的地址与端口，这样，服务器收到数据后，直接调用sendto()就可以把数据用UDP发给客户端。
        print('Received from %s:%s.' % addr)
        s.sendto(b'Hello, %s!' % data, addr)
        print(data)
        # 将 bytes 解码为字符串
        data_str = data.decode('utf-8')

        # 将字符串解析为 Python 字典
        data = json.loads(data_str)
        action = data["action"]
        print(action)

        if action == 'ip_period':
            ip_period_modify(data["ip_period"])

        if action == 'port_period':
            port_period_modify(data["port_period"])

        if action == 'node_period':
            node_period_modify(data["node_period"])

        # ip_period =
        # port_period = port_period_modify(data)
        # node_period = node_period_select(data)
        # traction_select =

udp_server_write_to_db()