### Git拉取与提交
1.拉取main分支
```shell
git clone git@github.com:righstar2020/br-cti-client.git
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
git pull origin main
#解决可能得冲突
#将分支代码合并到自己的任务分支(work1)
git add .
git commit -m "work1 merge main"
#推送更新到自己的分支
git push origin work1
```
### 库依赖说明
