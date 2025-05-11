#  防御方的分配策略
from scipy.optimize import minimize

def Defend(serverNum, servers):
    D_set = []
    A_strategy = []
    V_set = []
    for i in range(len(servers)):
        D_set.append(servers[i].getCommonRequest())
        V_set.append(servers[i].getCapacity())
        A_strategy.append(servers[i].getAttackRequest())
    print("D_set:", D_set)
    print("A_strategy:", A_strategy)
    print("V_set:", V_set)
    print(serverNum)
    D_strategy_ic, D_strategy_ik = calculate_defender_strategy(D_set, A_strategy, V_set, wc=0.01, num=serverNum)
    return D_strategy_ic, D_strategy_ik


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
                    ik.append(sum_1)
                D_strategy_ik.append(ik)
                D_strategy_ic.append(sum(ik))
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


#优化函数
def objective(D_set, R_set, Xic_set, Xie_set,num,i_bar,j_bar,wc,f):
    def u(x):
        term = 0
        for i in range(1,num+1):
            if 0<R_set[i]<i_bar:
                term = term + wc*(D_set[i]+x[i])
            if j_bar<=R_set[i]<=num:
                term = term + f
            if i_bar<=R_set[i]<j_bar:
                term = term + wc*(D_set[i]+x[i])*Xic_set[i]+sum(Xie_set[i])*f
        return -term
    return u


def calculate_A_strategy(A_MAX, D_set, A_strategy, V_set, wc, num):
    """
    计算迭代对应的 攻击策略
    :param D_set: 记录正常流量的集合
    :param A_strategy: 所要求解的存在（SQP优化中，需要给出对应的预设值？）——开始会有初始值，通过优化获得最终的解值
    :param V_set: 记录对应的处理能力
    :param wc:
    :param num: 服务器数量
    :return:
    """
    # 恶意总流量最大值
    # A_MAX = 3000
    v_sum = sum(V_set)
    res = []
    r_rank_set = Ranking(num,[0]*(num+1),D_set)
    for i in range(1,num+1):
        for j in range(i,num + 2):
            A_set = A_strategy[:]
            f = calculate_F(wc,i,j,V_set,D_set,A_strategy,num)
            ic,ik = calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)
            R_set = Ranking(num, A_set, D_set)
            cons = []
            cons.append({'type':'ineq','fun':constraint2(A_MAX)})
            for k in range(1,num+1):
                #所有ai都大于0
                cons.append({'type':'ineq','fun':constraint1(k)})
                if 0<R_set[k]<i:
                    cons.append({'type':'ineq','fun':constraint3(wc,f,D_set[k],k)})
                if i<=R_set[k]<j:
                    cons.append({'type':'ineq','fun':constraint4(wc,f,D_set[k],v_sum,k)})
                    cons.append({'type':'ineq','fun':constraint5(wc,f,D_set[k],k)})
                if j<=R_set[k]<=num:
                    cons.append({'type':'ineq','fun':constraint6(wc,f,D_set[k],v_sum,k)})
            for l in range(1,num+1):
                for ll in range(l,num+1):
                    if(r_rank_set[l]<r_rank_set[ll]):
                        cons.append({'type':'ineq','fun':constraint8(D_set,l,ll)})
                    elif(r_rank_set[l]>=r_rank_set[ll]):
                        cons.append({'type':'ineq','fun':constraint9(D_set,l,ll)})

            '''
            for m in range(1,num+1):
                #排序
                cons.append({'type':'eq','fun':constraint7(num,D_set,r_rank_set,m)})
            '''
            cons = tuple(cons)
            #print('cons\n',cons)
            r = minimize(objective(D_set,R_set,ic,ik,num,i,j,wc,f), A_strategy,method='SLSQP',constraints=cons)
            flag = 0
            for m in range(1,num+1):
                if r.x[m] <0:
                    flag = 1
                if sum(r.x)> A_MAX:
                    flag = 1
                #if Ranking(num,r.x,D_set) != R_set:
                    #flag = 1
            if flag == 0:
                res.append(r)
            #验证排序是否正确
            #s = res[-1]
            #print('正常流量：\n',R_set)
            #print('正常流量+恶意流量：\n',Ranking(num,s.x,D_set))
    print(res)
    #找到使得U（a,x）最大的解，也就是使得fun最小的解
    u = []
    for i in res:
        u.append(i.fun)
    print("最小值是%d,下标是%d"%(min(u),u.index(min(u))))
    print("success:?",res[u.index(min(u))].success)
    print("对应解：\n",res[u.index(min(u))].x)
    print('正常流量排名：\n',r_rank_set)
    print('正常流量+恶意流量排名：\n',Ranking(num,res[u.index(min(u))].x,D_set))
    print('攻击流量总和：',sum(res[u.index(min(u))].x))
    return res[u.index(min(u))].x

def constraint1(i):
    def v(x):
        return x[i]
    return v

def constraint2(A_MAX):
    def v(x):
        return A_MAX-sum(x[1:])
    return v

def constraint3(wc, f,d_i,i):
    def v(x):
        return wc/f - 1/(d_i + x[i])
    return v

def constraint4(wc,f,d_i,v_sum,i):
    def v(x):
        return 1/(d_i+x[i])-(wc-1/v_sum)/f
    return v

def constraint5(wc,f,d_i,i):
    def v(x):
        return wc/f - 1/(x[i]+d_i)
    return v

def constraint6(wc,f,d_i,v_sum,i):
    def v(x):
        return (wc-1/v_sum)/f - 1/(d_i+x[i])
    return v

def constraint7(num,D_set,r_rank_set,i):
    def v(x):
        rank_new = Ranking(num,x,D_set)
        return rank_new[i]-r_rank_set[i]
    return v

def constraint8(D_set,l,ll):
    def v(x):
        return x[ll]+D_set[ll]-x[l]-D_set[l]
    return v

def constraint9(D_set,l,ll):
    def v(x):
        return x[l]+D_set[l]-x[ll]-D_set[ll]
    return v

if __name__ == "__main__":
    D_set = [0, 50, 250, 500, 750, 1000]
    A_strategy = [0, 50, 250, 500, 750, 1000]
    V_set = [0, 50, 50, 100, 100, 200]
    #D_set = [0,50,300,550,800,1050,1300]
    #A_strategy = [0,10,10,10,10,10]
    #V_set = [0,50,100,200,400,800,1600]
    wc = 0.01
    num = 5
    #D_set = [0,1000,750,500,250,50]
    #A_strategy = [0,1000,750,500,250,50]
    #V_set = [0,200,100,100,50,50]
    #num = 5
    #R_set = [0,1,2,3,4,5]
    #ic, ik =calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)
    #num = 8
    #D_set = [0, 600,700,800,900,1000,1100,1200,1300]
    #A_strategy = [0,0,0,0,0,0,0,0,0]
    #A_strategy = [0,0,0,0,0,0,0,0,0,0,0]
    V_set = [0, 50, 50, 50, 50, 50, 50, 50, 50]
    #result = []

    #攻击策略
    A_strategy_new = calculate_A_strategy(D_set, A_strategy, V_set, wc, num)
    #防御策略
    ic, ik =calculate_defender_strategy(D_set, A_strategy_new, V_set, wc, num)
    print('根据攻击策略做出新的防御策略ic:',ic)
    print('根据攻击策略做出新的防御策略ik',ik)
    #res = minimize(objective(D_set,R_set,ic,ik,5,1,1,0.1,3), A_strategy)
    #print(res.fun)
    #print(res.success)
    #print(res.x)
    #ic, ik =calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)
    #print(ic)
    #print(ik)
