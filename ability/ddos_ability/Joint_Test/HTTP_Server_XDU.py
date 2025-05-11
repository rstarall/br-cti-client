from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from Connect_DB import *  # 确保这个模块包含了你需要的数据库处理函数

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data.decode('utf-8'))

        action = json_data.get("action")
        if action == 'ip_period':
            ip_period_modify(json_data["ip_period"])
            response = json.dumps({"status": "success", "action": action})
        elif action == 'port_period':
            port_period_modify(json_data["port_period"])
            response = json.dumps({"status": "success", "action": action})
        elif action == 'node_period':
            node_period_modify(json_data["node_period"])
            response = json.dumps({"status": "success", "action": action})
        else:
            response = json.dumps({"status": "error", "message": "Unknown action"})

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run(port=8080)