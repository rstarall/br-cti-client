# 1.开发说明

## 1.1 Git拉取与提交

1.拉取main分支

```shell
git clone https://github.com/righstar2020/br-cti-client.git
```

2.创建自己的任务分支(比如任务1)

```shell
git checkout -b work1
```
3.切换到自己的任务分支
```shell
git checkout work1
```
4.首次提交分支到远程仓库
```shell
git push origin work1
```
5.提交自己的代码到远程分支
```shell
git add .
git commit -m "work1 update commit"
git push -u origin work1
```
6.拉取某个分支的代码并合并到自己的开发分支
```shell
#拉取分支代码
git pull origin client #拉取data_client分支代码
#解决可能得冲突
#将分支代码合并到自己的任务分支(work1)
git add .
git commit -m "work1 merge main"
#推送更新到自己的分支
git push origin work1
```
7.子项目git
```shell
git submodule add https://github.com/righstar2020/br-cti-bc-server bc-server
```
更新子项目
```shell
 git submodule update –init –recursive
```
### 库依赖说明
使用fabric-go-sdk 2.2.0
需要使用 go 1.14编译 fabric-server
IPFS-Toolkit
```shell
pip install IPFS-Toolkit
```
## 1.2 Fabric说明
fabric证书文件夹ordererOrganizations、peerOrganizations
放在目录fabric-server\config下

## 1.3 IPFS说明
修改IPFS默认绑定地址教程:
https://blog.csdn.net/inthat/article/details/106212948
```shell
ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["http://taigu.xxx.cn:5002", "http://127.0.0.1:5001", "https://webui.ipfs.io"]'
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "POST"]'
```
启动IPFS(IPFS经常容易down)
```shell
nohup ipfs daemon &
```
IPFS Web
http://172.22.232.42:5001/webui
使用SSH端口转发访问
```shell
ssh -L 5001:localhost:5001 dev01@172.22.232.42
ssh -L 8080:127.0.0.1:8080 dev01@172.22.232.42
```

