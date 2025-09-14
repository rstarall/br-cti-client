import base64
import io
import matplotlib.pyplot as plt
import matplotlib as mpl
from ability.game_ability.Defend import calculate_defender_strategy, cost, single
from ability.game_ability.attack import calculate_A_strategy


class GameAbility:
    def __init__(self):
        # 设置中文字体
        mpl.rcParams['font.family'] = 'SimHei'

    def _plot_to_base64(self, fig):
        """将matplotlib图形转换为base64编码"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        return image_base64

    def _create_pie_chart(self, data, labels, colors, explode=None):
        """创建饼图"""
        fig, ax = plt.subplots(figsize=(8, 6))
        if explode is None:
            explode = (0.1, 0, 0, 0)
        ax.pie(data, labels=labels, colors=colors, autopct='%.2f%%', explode=explode)
        plt.tight_layout()
        return fig

    def _create_bar_chart(self, labels, values, colors=None):
        """创建柱状图"""
        if colors is None:
            colors = ['skyblue', 'orange']

        fig, ax = plt.subplots(figsize=(6, 5))
        bars = ax.bar(labels, values, width=0.2, color=colors)

        ax.set_xlabel('防御类型', fontsize=12)
        ax.set_ylabel('防御成本', fontsize=12)

        # 在每个柱子上方显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom')

        plt.tight_layout()
        return fig

    def calculate_ip_strategy(self, input1, input2, input3):
        """
        计算IP网络防御策略
        :param input1: 对节点1的攻击流量
        :param input2: 对节点2的攻击流量
        :param input3: 对节点3的攻击流量
        :return: 包含策略数据和图片base64的字典
        """
        try:
            D_set = [0, 5000, 5000, 5000]
            A_strategy = [0, input1, input2, input3]
            V_set = [0, 1120, 2002, 2980]
            wc = 0.0005
            num = 3

            # 计算防御策略
            ic, ik = calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)
            ipgamecost = round(cost(D_set, A_strategy, V_set, wc, ik, ic), 1)
            ipsinglecost = round(single(D_set, A_strategy, V_set, wc), 1)
            reduce = round(1 - ipgamecost / ipsinglecost, 3) * 100

            # 计算流量分配
            volumec = []
            volumek = []
            for i in range(num):
                volumec.append((D_set[i+1] + A_strategy[i+1]) * ic[i+1])
                kk = []
                for j in range(num):
                    kk.append((D_set[i+1] + A_strategy[i+1]) * (ik[i+1][j]))
                volumek.append(kk)

            allstrategy = []
            for i in range(num):
                strategy = []
                strategy.append(volumec[i])
                for j in range(num):
                    strategy.append(volumek[i][j])
                allstrategy.append(strategy)

            # 生成图片
            colors = ["#d5695d", "#5d8ca8", "#65a479", "#a564c9"]

            # 策略1饼图
            fig1 = self._create_pie_chart(
                allstrategy[0],
                ['云清洗', '本地过滤', 'B协同过滤', 'C协同过滤'],
                colors
            )
            strategy1_base64 = self._plot_to_base64(fig1)

            # 策略2饼图
            fig2 = self._create_pie_chart(
                allstrategy[1],
                ['云清洗', 'A协同过滤', '本地过滤', 'C协同过滤'],
                colors
            )
            strategy2_base64 = self._plot_to_base64(fig2)

            # 策略3饼图
            fig3 = self._create_pie_chart(
                allstrategy[2],
                ['云清洗', 'A协同过滤', 'B协同过滤', '本地过滤'],
                colors
            )
            strategy3_base64 = self._plot_to_base64(fig3)

            # 效果对比柱状图
            fig4 = self._create_bar_chart(
                ['独立防御', '协同博弈防御'],
                [ipsinglecost, ipgamecost]
            )
            effect_base64 = self._plot_to_base64(fig4)

            return {
                "status": "success",
                "data": {
                    "reduce": reduce,
                    "game_cost": ipgamecost,
                    "single_cost": ipsinglecost,
                    "input1": input1,
                    "input2": input2,
                    "input3": input3,
                    "images": {
                        "strategy1": strategy1_base64,
                        "strategy2": strategy2_base64,
                        "strategy3": strategy3_base64,
                        "effect": effect_base64
                    }
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"计算IP策略时发生错误: {str(e)}"
            }

    def calculate_5g_strategy(self, budget):
        """
        计算5G网络防御策略
        :param budget: 攻击者预算
        :return: 包含策略数据和图片base64的字典
        """
        try:
            D_set = [0, 4312, 5678, 6421]
            A_strategy = [0, budget/3, budget/3, budget/3]
            V_set = [0, 8200, 5320, 6700]
            wc = 0.0001
            num = 3

            # 计算攻击策略
            try:
                A_strategy_optimized = calculate_A_strategy(budget, D_set, A_strategy, V_set, wc, num)
                # 检查优化结果是否有效
                if A_strategy_optimized is not None and len(A_strategy_optimized) > 3:
                    A_strategy = A_strategy_optimized
                    atrategy1 = int(list(A_strategy)[1]) + D_set[1]
                    atrategy2 = int(list(A_strategy)[2]) + D_set[2]
                    atrategy3 = int(list(A_strategy)[3]) + D_set[3]
                else:
                    # 如果优化失败，使用平均分配策略
                    print("攻击策略优化失败，使用平均分配策略")
                    A_strategy = [0, budget/3, budget/3, budget/3]
                    atrategy1 = int(budget/3) + D_set[1]
                    atrategy2 = int(budget/3) + D_set[2]
                    atrategy3 = int(budget/3) + D_set[3]
            except Exception as e:
                print(f"攻击策略计算出错: {e}，使用平均分配策略")
                A_strategy = [0, budget/3, budget/3, budget/3]
                atrategy1 = int(budget/3) + D_set[1]
                atrategy2 = int(budget/3) + D_set[2]
                atrategy3 = int(budget/3) + D_set[3]

            # 计算防御策略
            ic, ik = calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)

            # 检查防御策略计算结果
            if ic is None or ik is None:
                return {
                    "status": "error",
                    "message": "防御策略计算失败，无法找到有效解"
                }

            ipgamecost = round(cost(D_set, A_strategy, V_set, wc, ik, ic), 1)
            ipsinglecost = round(single(D_set, A_strategy, V_set, wc), 1)
            reduce = round(1 - ipgamecost / ipsinglecost, 3) * 100

            # 计算流量分配
            volumec = []
            volumek = []
            for i in range(num):
                volumec.append((D_set[i+1] + A_strategy[i+1]) * ic[i+1])
                kk = []
                for j in range(num):
                    kk.append((D_set[i+1] + A_strategy[i+1]) * (ik[i+1][j]))
                volumek.append(kk)

            allstrategy = []
            for i in range(num):
                strategy = []
                strategy.append(volumec[i])
                for j in range(num):
                    strategy.append(volumek[i][j])
                allstrategy.append(strategy)

            # 生成图片
            colors = ["#d5695d", "#5d8ca8", "#65a479", "#a564c9"]
            attack_colors = ["#ffb84d", "#e74d3c", "#bf3a2b"]

            # 策略1饼图
            fig1 = self._create_pie_chart(
                allstrategy[0],
                ['云清洗', '本地过滤', 'B协同过滤', 'C协同过滤'],
                colors
            )
            strategy1_base64 = self._plot_to_base64(fig1)

            # 策略2饼图
            fig2 = self._create_pie_chart(
                allstrategy[1],
                ['云清洗', 'A协同过滤', '本地过滤', 'C协同过滤'],
                colors
            )
            strategy2_base64 = self._plot_to_base64(fig2)

            # 策略3饼图
            fig3 = self._create_pie_chart(
                allstrategy[2],
                ['云清洗', 'A协同过滤', 'B协同过滤', '本地过滤'],
                colors
            )
            strategy3_base64 = self._plot_to_base64(fig3)

            # 攻击策略饼图
            fig4 = self._create_pie_chart(
                A_strategy[1:],
                ['向A进攻', '向B进攻', '向C进攻'],
                attack_colors,
                explode=(0, 0, 0)
            )
            attacker_base64 = self._plot_to_base64(fig4)

            # 效果对比柱状图
            fig5 = self._create_bar_chart(
                ['独立防御', '协同博弈防御'],
                [ipsinglecost, ipgamecost]
            )
            effect_base64 = self._plot_to_base64(fig5)

            return {
                "status": "success",
                "data": {
                    "reduce": reduce,
                    "game_cost": ipgamecost,
                    "single_cost": ipsinglecost,
                    "budget": budget,
                    "atrategy1": atrategy1,
                    "atrategy2": atrategy2,
                    "atrategy3": atrategy3,
                    "images": {
                        "strategy1": strategy1_base64,
                        "strategy2": strategy2_base64,
                        "strategy3": strategy3_base64,
                        "attacker": attacker_base64,
                        "effect": effect_base64
                    }
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"计算5G策略时发生错误: {str(e)}"
            }

    def calculate_satellite_strategy(self):
        """
        计算卫星网络防御策略
        :return: 包含策略数据和图片base64的字典
        """
        try:
            # 卫星网络参数
            D_set = [0, 5000, 5000, 5000]
            A_strategy = [0, 13000, 18000, 20000]
            V_set = [0, 1000, 2000, 3000]
            wc = 0.001
            num = 3

            # 计算防御策略
            ic, ik = calculate_defender_strategy(D_set, A_strategy, V_set, wc, num)
            ipgamecost = round(cost(D_set, A_strategy, V_set, wc, ik, ic), 1)
            ipsinglecost = round(single(D_set, A_strategy, V_set, wc), 1)
            reduce = round(1 - ipgamecost / ipsinglecost, 3) * 100

            # 计算流量分配
            volumec = []
            volumek = []
            for i in range(num):
                volumec.append((D_set[i+1] + A_strategy[i+1]) * ic[i+1])
                kk = []
                for j in range(num):
                    kk.append((D_set[i+1] + A_strategy[i+1]) * (ik[i+1][j]))
                volumek.append(kk)

            allstrategy = []
            for i in range(num):
                strategy = []
                strategy.append(volumec[i])
                for j in range(num):
                    strategy.append(volumek[i][j])
                allstrategy.append(strategy)

            # 生成图片
            colors = ["#d5695d", "#5d8ca8", "#65a479", "#a564c9"]

            # 策略1饼图
            fig1 = self._create_pie_chart(
                allstrategy[0],
                ['云清洗', '本地过滤', 'B协同过滤', 'C协同过滤'],
                colors
            )
            strategy1_base64 = self._plot_to_base64(fig1)

            # 策略2饼图
            fig2 = self._create_pie_chart(
                allstrategy[1],
                ['云清洗', 'A协同过滤', '本地过滤', 'C协同过滤'],
                colors
            )
            strategy2_base64 = self._plot_to_base64(fig2)

            # 策略3饼图
            fig3 = self._create_pie_chart(
                allstrategy[2],
                ['云清洗', 'A协同过滤', 'B协同过滤', '本地过滤'],
                colors
            )
            strategy3_base64 = self._plot_to_base64(fig3)

            # 效果对比柱状图
            fig4 = self._create_bar_chart(
                ['独立防御', '协同博弈防御'],
                [ipsinglecost, ipgamecost]
            )
            effect_base64 = self._plot_to_base64(fig4)

            return {
                "status": "success",
                "data": {
                    "reduce": reduce,
                    "game_cost": ipgamecost,
                    "single_cost": ipsinglecost,
                    "images": {
                        "strategy1": strategy1_base64,
                        "strategy2": strategy2_base64,
                        "strategy3": strategy3_base64,
                        "effect": effect_base64
                    }
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"计算卫星策略时发生错误: {str(e)}"
            }
