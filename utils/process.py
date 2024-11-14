import subprocess
# 定义全局变量来存储运行中的进程
global running_process
running_process = None
def run_program(exe_path,args_list,cwd=None):
    # 使用 subprocess.Popen 启动 .exe 程序
    # 假设你的 .exe 文件名为 'myprogram.exe'
   # 构建完整的命令列表，包括程序路径和参数
    command = [exe_path] + args_list
    #指定工作目录
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=cwd)
    
    # 存储进程对象以便稍后可以终止它
    global running_process
    running_process = process
    
    # 等待程序结束
    stdout, stderr = process.communicate()
    print(f"Program finished with exit code {process.returncode}")
    if stdout:
        print(f"STDOUT: {stdout.decode()}")
    if stderr:
        print(f"STDERR: {stderr.decode()}")

def stop_program():
    global running_process
    if running_process and running_process.poll() is None:  # 检查进程是否还在运行
        running_process.terminate()  # 发送 SIGTERM
        try:
            running_process.wait(timeout=5)  # 等待进程优雅地退出
        except subprocess.TimeoutExpired:
            running_process.kill()  # 如果进程没有在5秒内退出，则强制杀死它
            running_process.wait()
    print("Child process terminated.")