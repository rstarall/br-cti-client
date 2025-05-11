import socket
# from Connect_DB import *
"""
使用UDP的通信双方也分为客户端和服务器。
服务器首先需要绑定端口：
"""
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# 绑定端口:
s.bind(('127.0.0.1', 9998))

print('Bind UDP on 9998...')

while True:
    # 接收数据:
    data, addr = s.recvfrom(1024)
    # recvfrom()方法返回数据和客户端的地址与端口，这样，服务器收到数据后，直接调用sendto()就可以把数据用UDP发给客户端。
    print('Received from %s:%s.' % addr)
    s.sendto(b'Hello, %s!' % data, addr)

    # connect_db()
    # if
    # ip_period = ip_period_modify()
    # port_period = port_period_modify()
    # node_period = node_period_select()
    #
    #