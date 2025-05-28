from flask import Flask, render_template, request
from Defend import calculate_defender_strategy, cost, single
from Attack import calculate_A_strategy
from plot import plotIP,plot5G

app = Flask(__name__)

#主页面
@app.route('/',methods=['GET','POST'])
def page():
    return render_template('page.html')


#IP网络页面后端
@app.route('/IP',methods=['GET','POST'])
def IP():
    reduce=None
    input1=None
    input2=None
    input3=None

    #读到输入后执行，计算防守策略以及画图，画完图后传递参数重新渲染页面
    if request.method == 'POST':
        # 获取表单数据
        input1 = int(request.form.get('IPinput1'))
        input2 = int(request.form.get('IPinput2'))
        input3 = int(request.form.get('IPinput3'))

        D_set = [0, 5000, 5000, 5000]
        A_strategy = [0, input1, input2, input3]
        V_set = [0,1120,2002,2980]
        wc = 0.0005
        num = 3
        ic,ik=calculate_defender_strategy(D_set,A_strategy,V_set,wc,num)
        ipgamecost=round(cost(D_set,A_strategy,V_set,wc,ik,ic),1)
        ipsinglecost=round(single(D_set,A_strategy,V_set,wc),1)
        reduce = round(1 - ipgamecost / ipsinglecost,3)*100

        #画图
        plotIP(D_set,A_strategy,ic,ik,num,ipgamecost,ipsinglecost)

    return render_template('IP.html',reduce=reduce,input1=input1,input2=input2,input3=input3)

#5G网络页面后端
@app.route('/5G',methods=['GET','POST'])
def page5G():
    reduce = None
    budget=None
    atrategy1=None
    atrategy2=None
    atrategy3=None

    # 读到输入后执行，计算防守策略进攻策略以及画图，画完图后传递参数重新渲染页面
    if request.method == 'POST':
        budget = int(request.form.get('5Ginput'))
        D_set = [0, 4312,5678,6421]
        A_strategy = [0, budget/3, budget/3, budget/3]
        V_set = [0,8200,5320,6700]
        wc = 0.0001
        num = 3
        A_strategy = calculate_A_strategy(budget, D_set, A_strategy, V_set, wc, num)
        atrategy1 = int(list(A_strategy)[1])+D_set[1]
        atrategy2 = int(list(A_strategy)[2])+D_set[2]
        atrategy3 = int(list(A_strategy)[3])+D_set[3]
        print("gongjicelve")
        ic,ik=calculate_defender_strategy(D_set,A_strategy,V_set,wc,num)
        ipgamecost=round(cost(D_set,A_strategy,V_set,wc,ik,ic),1)
        ipsinglecost=round(single(D_set,A_strategy,V_set,wc),1)
        reduce=round(1-ipgamecost/ipsinglecost,3)*100

        # 画图
        plot5G(D_set,A_strategy,ic,ik,num,ipgamecost,ipsinglecost)

    return render_template('5G.html',reduce=reduce,budget=budget,atrategy1=atrategy1
                           ,atrategy2=atrategy2,atrategy3=atrategy3)

#卫星网络页面后端
@app.route('/sate')
def sate():
    return render_template('sate.html')




if __name__ == '__main__':
    app.run(debug=True)