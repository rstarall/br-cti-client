from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# 假设这些函数是你原来的数据处理逻辑
def ip_period_modify():
    # 这里应该返回处理后的IP信息，但为了示例，我们返回一个静态字符串
    return "192.168.1.1"

def port_period_modify():
    # 这里应该返回处理后的端口信息，但为了示例，我们返回一个静态字符串（数字形式）
    return "8080"

def node_period_select():
    # 这里应该返回选中的节点信息，但为了示例，我们返回一个静态字符串
    return "node1"

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析查询参数（如果有的话）
        # 但在这个示例中，我们不会实际使用查询参数，而是直接返回处理后的数据
        
        # 构建响应数据
        response_data = {
            "ip_period": ip_period_modify(),
            "port_period": port_period_modify(),
            "node_period": node_period_select()
        }
        
        # 将响应数据转换为JSON字符串
        response_body = json.dumps(response_data).encode('utf-8')
        
        # 发送响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response_body)

def run(server_class=HTTPServer, handler_class=MyHandler, port=9998):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting HTTP server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run(port=9998)