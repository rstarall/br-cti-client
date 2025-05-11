from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 发送HTTP响应状态码
        self.send_response(200)
        # 发送HTTP响应头
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # 发送HTTP响应体
        self.wfile.write(b"Hello, this is an HTTP server!")

def run(server_class=HTTPServer, handler_class=MyHandler, port=9998):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run(port=9998)