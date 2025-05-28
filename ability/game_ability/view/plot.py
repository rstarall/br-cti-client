import matplotlib.pyplot as plt
import matplotlib as mql
import numpy as np

def plotIP(D_set,A_strategy,ic,ik,num,cost,single):
    volumec=[]
    volumek=[]
    for i in range(num):
        volumec.append((D_set[i+1]+A_strategy[i+1])*ic[i+1])
        kk=[]
        for j in range(num):
            kk.append((D_set[i+1]+A_strategy[i+1])*(ik[i+1][j]))
        volumek.append(kk)
    allstrategy=[]
    for i in range(num):
        strategy=[]
        strategy.append(volumec[i])
        for j in range(num):
            strategy.append(volumek[i][j])
        allstrategy.append(strategy)
    mql.rcParams['font.family']='SimHei'

    plt.clf()
    plt.pie(allstrategy[0],labels=['云清洗','本地过滤','B协同过滤','C协同过滤'],colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.tight_layout()
    plt.savefig('static/IP/ip-strategy-1-dynamic.png',dpi=300)
    plt.clf()

    plt.pie(allstrategy[1],labels=['云清洗','A协同过滤','本地过滤','C协同过滤'],colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.tight_layout()
    plt.savefig('static/IP/ip-strategy-2-dynamic.png',dpi=300)
    plt.clf()

    plt.pie(allstrategy[2], labels=['云清洗','A协同过滤', 'B协同过滤', '本地过滤'],
            colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.tight_layout()
    plt.savefig('static/IP/ip-strategy-3-dynamic.png',dpi=300)
    plt.clf()


    labels = ['独立防御', '协同博弈防御']
    values = [single, cost]  # 每种防御类型的值

    # 创建图形
    fig, ax = plt.subplots(figsize=(6, 5))

    # 绘制条形图（单组柱子）
    bars = ax.bar(labels, values, width=0.2, color=['skyblue', 'orange'])

    # 添加标题和标签

    ax.set_xlabel('防御类型', fontsize=12)
    ax.set_ylabel('防御成本', fontsize=12)

    # 在每个柱子上方显示数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}',
                ha='center', va='bottom')

    # 设置y轴范围（可选）

    # 显示图形
    plt.tight_layout()
    plt.savefig('static/IP/IPeffect-dynamic.png',dpi=300)
    return

def plot5G(D_set,A_strategy,ic,ik,num,cost,single):
    volumec=[]
    volumek=[]
    for i in range(num):
        volumec.append((D_set[i+1]+A_strategy[i+1])*ic[i+1])
        kk=[]
        for j in range(num):
            kk.append((D_set[i+1]+A_strategy[i+1])*(ik[i+1][j]))
        volumek.append(kk)
    allstrategy=[]
    for i in range(num):
        strategy=[]
        strategy.append(volumec[i])
        for j in range(num):
            strategy.append(volumek[i][j])
        allstrategy.append(strategy)
    mql.rcParams['font.family']='SimHei'

    plt.clf()
    plt.pie(allstrategy[0],labels=['云清洗','本地过滤','B协同过滤','C协同过滤'],colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.tight_layout()
    plt.savefig('static/5G/5g-strategy-1-dynamic.png',dpi=300)
    plt.clf()

    plt.pie(allstrategy[1],labels=['云清洗','A协同过滤','本地过滤','C协同过滤'],colors=["#d5695d", "#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.savefig('static/5G/5g-strategy-2-dynamic.png',dpi=300)
    plt.clf()

    plt.pie(allstrategy[2], labels=['云清洗','A协同过滤', 'B协同过滤', '本地过滤'],
            colors=["#d5695d","#5d8ca8", "#65a479", "#a564c9"],
            autopct='%.2f%%',explode=(0.1, 0, 0,0))
    plt.tight_layout()
    plt.savefig('static/5G/5g-strategy-3-dynamic.png',dpi=300)
    plt.clf()

    plt.pie(A_strategy[1:], labels=['向A进攻', '向B进攻', '向C进攻'],
            colors=["#ffb84d","#e74d3c", "#bf3a2b"],
            autopct='%.2f%%')
    plt.tight_layout()
    plt.savefig('static/5G/5g-attacker-dynamic.png',dpi=300)

    labels = ['独立防御', '协同博弈防御']
    values = [single, cost]  # 每种防御类型的值

    # 创建图形
    fig, ax = plt.subplots(figsize=(6, 5))

    # 绘制条形图（单组柱子）
    bars = ax.bar(labels, values, width=0.2, color=['skyblue', 'orange'])

    # 添加标题和标签

    ax.set_xlabel('防御类型', fontsize=12)
    ax.set_ylabel('防御成本', fontsize=12)

    # 在每个柱子上方显示数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}',
                ha='center', va='bottom')

    # 设置y轴范围（可选）

    # 显示图形
    plt.tight_layout()
    plt.savefig('static/5G/5Geffect-dynamic.png',dpi=300)
    plt.clf()
    return


# def plotsate():
#     plt.pie([11000,7000],labels=['本地过滤','C协同过滤'],colors=["#5d8ca8", "#a564c9"],
#                 autopct='%.2f%%')
#     plt.savefig('static/sate/sate-strategy-1-dynamic.png',dpi=300)
#     plt.show()
#     plt.pie([22000,1000],labels=['本地过滤','C协同过滤'],colors=["#65a479", "#a564c9"],
#                 autopct='%.2f%%')
#     plt.savefig('static/sate/sate-strategy-2-dynamic.png',dpi=300)
#     plt.show()
#     plt.pie([1], labels=['本地过滤'],
#                 colors=["#a564c9"],
#                 autopct='%.2f%%')
#     plt.savefig('static/sate/sate-strategy-3-dynamic.png',dpi=300)
#     plt.show()

if __name__ == '__main__':
    D_set = [0, 5000, 5000, 5000]
    A_strategy = [0, 15000, 20000, 25000]
    V_set = [0,1120,2002,2980]
    wc = 0.0005
    num = 3
    cost=40.4
    single=28.2
    ic=[0, 0.7372500000000003, 0.17960000000000031, 0]
    ik=[[], [0.04822681088167808, 0.08620542445099957, 0.12831776466732203], [0.15058144870534246, 0.26916433956079966, 0.40065421173385757], [0.18354637823664371, 0.32808915109800063, 0.4883644706653556]]

    plot5G(D_set,A_strategy,ic,ik,num,cost,single)