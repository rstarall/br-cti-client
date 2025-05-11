import subprocess

# 定义要添加的 iptables 规则
rule = "-A INPUT -p tcp --dport 80 -j ACCEPT"

# 使用 subprocess.run 来执行 iptables 命令
# 注意：这里假设你有足够的权限来修改 iptables 规则，通常这需要 root 权限
result = subprocess.run(["iptables", rule], capture_output=True, text=True)

# 检查命令执行结果
if result.returncode == 0:
    print("iptables 规则添加成功")
else:
    print(f"iptables 规则添加失败: {result.stderr}")