

### Git拉取与提交
拉取main分支
```shell
git clone git@github.com:righstar2020/br-cti-client.git
```
创建自己的任务分支(比如任务1)
```shell
git checkout -b dev
```
切换到自己的任务分支
```shell
git checkout dev
```
首次提交分支到远程仓库
```shell
git push origin dev
```
提交自己的代码到远程分支
```shell
git add .
git commit -m "work1 update commit"
git push -u origin dev
```