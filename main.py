
from server.app import app
from utils.process import run_program, stop_program
from utils.file import get_project_root_path
import threading

def start_fabric_server(): 
    print("-------------启动 fabric Server服务----------------------")
    fabric_server_pwd = get_project_root_path()+"/fabric-server"
    program_path = fabric_server_pwd+"/fabric-server.exe"
    # 创建并启动线程来运行程序
    args_list=[] #程序参数['--port','7777']可为空
    program_thread = threading.Thread(target=run_program, args=(program_path,args_list),kwargs={'cwd': fabric_server_pwd})
    program_thread.start()
def wait_stop_fabric_server(): 
    print("-------------等待停止 fabric Server服务----------------------")
    stop_program()
def start_flask_server():
    print("-------------启动 flask服务----------------------")
    #注意：use_reloader=False 防止重载时创建多个事件循环 
    app.run(host="127.0.0.1",port=5000,debug=False, use_reloader=False)

if __name__ == '__main__':
    start_fabric_server()
    start_flask_server()
    wait_stop_fabric_server()