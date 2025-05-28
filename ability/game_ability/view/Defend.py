#  防御方的分配策略
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib as mql
import numpy as np

def make_autopct(value):
    def my_autopct(pct):
        total =sum(value)
        val = int(round(pct*total/100.0))
        return '{p:.2f}% ({v:d})'.format(p=pct,v=val)
    return my_autopct

def calculate_F(wc, num_i, num_j, V_set, D_set, A_strategy, num):
    """
    @:param
    num 防御者数目
    wc (float) 云服务器，单位流量传输到云的传输延迟的系数
    num_i、num_j 枚举获得的对应的防御者编号
    V_set (list) 各边缘服务器的集合，可存放对应服务器处理流量的能力的fk
    D_set (list) 防御者集合,存放所有防御者（通过枚举 D_set 产生i,j）,可存放正常流量的值
    A_strategy (list) 攻击者策略
    :return:
    """
    # 计算对应的逻辑，这里的eg:num_i = 3, num_j = 5 ,这是传递到函数里供计算使用的值，
    # 考虑集合中对应的下标就是对应的值，更改对应的存储的集合的方式
    # num_i <= num_j 不发生越界问题
    sum1 = sum(
        (D_set[i] + A_strategy[i]) * wc for i in range(num_i, num_j))  # [num_i ,num_j)  实际上就是num_i~num_j-1的数 符合公式的求和区间

    # [num_j,num+1)
    # 最后一个索引的值是数组最后一个值，当传入的num_j = num+1时，也不会发生越界行为
    sum2 = sum((D_set[i] + A_strategy[i]) / sum(V_set) for i in range(num_j, num + 1))

    F = (sum1 + sum2) / (num_j - num_i + 1)
    return F


def Ranking(num, A_strategy, D_set):
    sum_list = [A_strategy[i] + D_set[i] for i in range(1, num + 1)]
    sorted_indices = sorted(range(len(sum_list)), key=lambda k: sum_list[k])
    R_set = [x + 1 for x in sorted_indices]
    R_set.insert(0, 0)
    return R_set


def judge(num_i, num_j, F, R_set, num, D_set, A_strategy, wc, m, s, sum1):
    """
    计算i,j是不是最终结果
    :param num_i: 对应的是排名值，num_i是从 1 开始遍历的，考虑的是左闭右闭[1,D_set]
    :param num_j:
    :param F:
    :param R_set: 每个索引值编号对应的排名rink ,按升序进行排列
    :param num: D的元素个数
    :return: bool
    """
    if num_i == 1:
        if num_j == 1:
            # 计算是否符合不等式
            if (1 / (D_set[s] + A_strategy[s])) <= sum1:
                return True
        elif num_j == num + 1:
            # 计算是否符合不等式
            if (1 / (D_set[m] + A_strategy[m])) > sum1:
                return True
        else:
            k = R_set.index(num_j)
            j = R_set.index(R_set[k] - 1)
            if (1 / (D_set[j] + A_strategy[j])) > sum1 >= (1 / (D_set[k] + A_strategy[k])):
                return True
    else:
        i = R_set.index(num_i)
        j = R_set.index(R_set[i] - 1)
        if (1 / (D_set[i] + A_strategy[i])) < (wc / F) <= (1 / (D_set[j] + A_strategy[j])):
            if num_j == 1:
                # 计算是否符合不等式
                if (1 / (D_set[s] + A_strategy[s])) <= sum1:
                    return True
            elif num_j == num + 1:
                # 计算是否符合不等式
                if (1 / (D_set[m] + A_strategy[m])) > sum1:
                    return True
            else:
                k = R_set.index(num_j)
                jj = R_set.index(R_set[k] - 1)
                if (1 / (D_set[jj] + A_strategy[jj])) > sum1 >= (1 / (D_set[k] + A_strategy[k])):
                    return True
    return False


def calculate_defender_strategy(D_set, A_strategy, V_set, wc, num):
    """
    @:param
    D_set (list) 防御者集合,存放所有防御者（通过枚举 D_set 产生i,j）,可存放正常流量的值
    A_strategy (list) 攻击者策略
    V_set (list) 各边缘服务器的集合，可存放对应服务器处理流量的能力的fk
    wc (float) 云服务器，单位流量传输到云的传输延迟的系数
    R_set (list) 记录每个defender对应的rank
    :return:
    """
    R_set = Ranking(num, A_strategy, D_set)
    true_i = -1
    true_j = -1
    flag = False

    # 计算拥有最大可疑流量服务器 m
    m = 0
    MIN_FLOW = -1
    flow_min = MIN_FLOW
    for i in range(1, num + 1):
        if flow_min < A_strategy[i] + D_set[i]:
            m = i
            flow_min = A_strategy[i] + D_set[i]

    # 计算拥有最小可疑流量服务器 s
    s = 0
    MAX_FLOW = 100000
    flow = MAX_FLOW + 1
    for i in range(1, num + 1):
        if flow > A_strategy[i] + D_set[i]:
            s = i
            flow = A_strategy[i] + D_set[i]

    # 枚举i，j后进行判断
    for i in range(1, num+1):
        for j in range(i, num + 2):
            f = calculate_F(wc, i, j, V_set, D_set, A_strategy, num)
            sum1 = wc - (1 / sum(V_set))
            sum1 = sum1 / f
            # 判断是否符合
            if judge(i, j, f, R_set, num, D_set, A_strategy, wc, m, s, sum1):
                true_i = i
                true_j = j
                flag = True
                break
                # 利用获得的F,i,j计算对应的策略
    if flag:
        # 计算对应的策略
        f = calculate_F(wc, true_i, true_j, V_set, D_set, A_strategy, num)
        D_strategy_ic = []
        D_strategy_ik = []
        for i in range(1, num + 1):
            if 0 < R_set[i] < true_i:
                D_strategy_ic.append(1)
                ik = []
                for k in range(1, len(V_set)):
                    ik.append(0)
                D_strategy_ik.append(ik)
            elif true_i <= R_set[i] < true_j:
                ik = []
                for k in range(1, len(V_set)):
                    sum_1 = wc * (D_set[i] + A_strategy[i]) - f
                    sum_1 = sum_1 * V_set[k] / (D_set[i] + A_strategy[i])
                    if(sum_1)<0:
                        sum_1=0
                    ik.append(sum_1)
                D_strategy_ik.append(ik)
                if (1 - sum(ik))<0:
                    D_strategy_ic.append(0)
                else:
                    D_strategy_ic.append(1-sum(ik))


            elif true_j <= R_set[i] <= num:
                D_strategy_ic.append(0)
                ik = []
                sum_V = sum(V_set)
                for k in range(1, len(V_set)):
                    sum_1 = V_set[k] / sum_V
                    ik.append(sum_1)
                D_strategy_ik.append(ik)

        D_strategy_ic.insert(0, 0)
        D_strategy_ik.insert(0, [])
        return D_strategy_ic, D_strategy_ik

def single(D_set,A_strategy,V_set,wc):
    sum=0
    for i in range(len(D_set)-1):
        sum=sum+(D_set[i+1]+A_strategy[i+1])/V_set[i+1]
    return sum

def cost(D_set,A_strategy,V_set,wc,ik,ic):
    f=0
    value=0
    for i in range(len(D_set)-1):
        f=f+(D_set[i+1]+A_strategy[i+1])*sum(ik[i+1])/sum(V_set)
    for i in range(len(D_set) - 1):
        value=value+(D_set[i+1]+A_strategy[i+1])*ic[i+1]*wc
        value=value+sum(ik[i+1])*f
    return value

if __name__ == "__main__":
    """
        @:param
        D_set (list) 防御者集合,存放所有防御者的正常流量的值，数据类型列表，第一个值占位无意义
        A_strategy (list) 攻击者策略，对各个防御者的投放的有害流量，数据类型列表，第一个值占位无意义
        V_set (list) 各边缘服务器的集合，存放对应服务器处理流量的能力，数据类型列表，第一个值占位无意义
        wc (float) 云服务器，单位流量传输到云的传输延迟的系数
        A_MAX 进攻者预算
        输出ic，各个防御者向云端转移的流量的百分比，数据类型列表，第一个值占位无意义
        输出ik，各个防守者向各个服务器转移的流量的百分比，数据类型二维列表，第一个值占位无意义
    """
    #ip平均流量3w
    D_set = [0, 5000, 5000, 5000]
    A_strategy = [0, 15000, 20000, 25000]
    V_set = [0,1120,2002,2980]
    wc = 0.0005
    num = 3

    #5G平均流量5W，云较快
    # D_set = [0, 5000, 5000, 5000]
    # A_strategy = [0, 35000, 45000, 55000]
    # V_set = [0, 8200,5320,6700]
    # wc = 0.0001
    # num = 3


    #卫星网络平均流量2w，云较慢
    # D_set = [0, 5000, 5000, 5000]
    # A_strategy = [0, 13000, 18000, 20000]
    # V_set = [0,1000,2000,3000]
    # wc = 0.001
    # num = 3


    #防御策略
    ic, ik =calculate_defender_strategy(D_set, A_strategy, V_set, wc=wc, num=num)
    print('根据攻击策略做出新的防御策略ic:',ic)
    print('根据攻击策略做出新的防御策略ik',ik)

    volumec=[]
    volumek=[]
    for i in range(num):
        volumec.append((D_set[i+1]+A_strategy[i+1])*ic[i+1])
        kk=[]
        for j in range(num):
            kk.append((D_set[i+1]+A_strategy[i+1])*(ik[i+1][j]))
        volumek.append(kk)
    print("分配到云的流量为：",volumec)
    print("协同防御的流量为：",volumek)


    print("博弈处理成本",cost(D_set,A_strategy,V_set,wc,ik,ic))


    print("单独处理成本",single(D_set,A_strategy,V_set,wc))

    allstrategy=[]
    for i in range(num):
        strategy=[]
        strategy.append(volumec[i])
        for j in range(num):
            strategy.append(volumek[i][j])
        allstrategy.append(strategy)
    mql.rcParams['font.family']='SimHei'


