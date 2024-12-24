import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # 设置后端为非交互式


def save_regression_plot(y_test, y_pred, save_dir, request_id):
    """
    保存回归模型评估图表
    params:
        - y_test: 测试集真实值
        - y_pred: 预测值
        - save_dir: 保存目录
        - request_id: 请求ID
    return:
        - str: 图像保存路径
    """
    try:
        # 创建1x3的子图布局
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
        
        # 设置字体大小
        plt.rcParams['font.size'] = 14  # 默认字体大小
        plt.rcParams['axes.titlesize'] = 16  # 标题字体大小
        plt.rcParams['axes.labelsize'] = 14  # 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 12  # x轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 12  # y轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 12  # 图例字体大小
        
        # 1. 预测值vs实际值散点图
        ax1.scatter(y_test, y_pred, alpha=0.5)
        ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax1.set_xlabel('实际值')
        ax1.set_ylabel('预测值')
        ax1.set_title('预测值 vs 实际值')
        
        # 2. 残差图
        residuals = y_test - y_pred
        ax2.scatter(y_pred, residuals, alpha=0.5)
        ax2.axhline(y=0, color='r', linestyle='--')
        ax2.set_xlabel('预测值')
        ax2.set_ylabel('残差')
        ax2.set_title('残差分布图')
        
        # 3. 预测值和实际值的分布对比
        ax3.hist(y_test, bins=30, alpha=0.5, label='实际值', edgecolor='black')
        ax3.hist(y_pred, bins=30, alpha=0.5, label='预测值', edgecolor='black')
        ax3.set_xlabel('值')
        ax3.set_ylabel('频数')
        ax3.set_title('预测值和实际值分布对比')
        ax3.legend()
        
        plt.tight_layout()
        save_path = os.path.join(save_dir, f'{request_id}_regression_eval.png')
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        print(f"保存回归评估图表时发生错误: {str(e)}")
        return None

def save_classification_plot(y_test, y_pred, save_dir, request_id):
    """
    保存分类模型评估图表
    params:
        - y_test: 测试集真实值
        - y_pred: 预测值
        - save_dir: 保存目录
        - request_id: 请求ID
    return:
        - str: 图像保存路径
    """
    try:
        # 创建1x3的子图布局
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
        
        # 设置字体大小
        plt.rcParams['font.size'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        
        # 获取所有唯一的类别标签
        all_classes = np.unique(np.concatenate([y_test, y_pred]))
        
        # 修改混淆矩阵计算
        cm = confusion_matrix(y_test, y_pred, labels=all_classes)
        
        # 1. 混淆矩阵热力图
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
        ax1.set_title('混淆矩阵')
        ax1.set_xlabel('预测类别')
        ax1.set_ylabel('实际类别')
        
        # 2. 每个类别的准确率柱状图
        class_accuracy = cm.diagonal() / cm.sum(axis=1)
        x = np.arange(len(all_classes))
        ax2.bar(x, class_accuracy)
        ax2.set_title('各类别准确率')
        ax2.set_xlabel('类别')
        ax2.set_ylabel('准确率')
        ax2.set_ylim(0, 1.1)
        ax2.set_xticks(x)
        ax2.set_xticklabels(all_classes)
        # 添加数值标签
        for i, v in enumerate(class_accuracy):
            ax2.text(i, v, f'{v:.2f}', ha='center', va='bottom')
        
        # 3. 预测分布与实际分布对比柱状图
        width = 0.35
        x = np.arange(len(all_classes))
        
        # 计算每个类别的样本数
        true_counts = np.zeros(len(all_classes))
        pred_counts = np.zeros(len(all_classes))
        
        for i, c in enumerate(all_classes):
            true_counts[i] = np.sum(y_test == c)
            pred_counts[i] = np.sum(y_pred == c)
        
        ax3.bar(x - width/2, true_counts, width, label='实际分布', alpha=0.8)
        ax3.bar(x + width/2, pred_counts, width, label='预测分布', alpha=0.8)
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(all_classes)
        ax3.set_title('类别分布对比')
        ax3.set_xlabel('类别')
        ax3.set_ylabel('样本数')
        ax3.legend()
        
        plt.tight_layout()
        save_path = os.path.join(save_dir, f'{request_id}_classification_eval.png')
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        print(f"保存分类评估图表时发生错误: {str(e)}")
        return None

def save_clustering_plot(X, y_pred, save_dir, request_id):
    """
    保存聚类模型评估图表
    params:
        - X: 特征数据
        - y_pred: 预测的聚类标签
        - save_dir: 保存目录
        - request_id: 请求ID
    return:
        - str: 图像保存路径
    """
    try:
        # 设置中文字体和字体大小
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建1行2列的子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        
        # 第一个子图: 原始特征空间(使用方差最大的两个原始特征绘图)
        print(f"Input shapes - X: {X.shape}, y_pred: {len(y_pred)}")
        X_df = pd.DataFrame(X)
        feature_vars = X_df.var()
        top_features = feature_vars.nlargest(2).index
        
        # 确保数据维度匹配
        plot_data = X_df[[top_features[0], top_features[1]]].values
        if len(plot_data) == len(y_pred):
            scatter1 = ax1.scatter(plot_data[:, 0], plot_data[:, 1], 
                                 c=y_pred, cmap='viridis')
        else:
            print(f"数据维度不匹配: X shape = {plot_data.shape}, y_pred length = {len(y_pred)}")
            return plot_error_figure(save_dir, request_id ,error_msg="数据维度不匹配")

        ax1.set_title('原始特征空间聚类结果')
        ax1.set_xlabel(f'特征 {top_features[0]}')
        ax1.set_ylabel(f'特征 {top_features[1]}')
        plt.colorbar(scatter1, ax=ax1)
        
        # 第二个子图: 轮廓系数或聚类样本分布
        if len(np.unique(y_pred)) > 1:  # 确保有多个簇
            try:
                silhouette_vals = silhouette_samples(X, y_pred)
                n_clusters = len(np.unique(y_pred))
                y_lower = 0
                
                for i in range(n_clusters):
                    cluster_silhouette_vals = silhouette_vals[y_pred == i]
                    cluster_silhouette_vals.sort()
                    size_cluster_i = len(cluster_silhouette_vals)
                    y_upper = y_lower + size_cluster_i

                    ax2.fill_betweenx(np.arange(y_lower, y_upper),
                                    0, cluster_silhouette_vals,
                                    alpha=0.7)
                    
                    y_lower = y_upper + 10  # 在簇之间添加间隔
                
                # 计算平均轮廓系数
                avg_silhouette = np.mean(silhouette_vals)
                ax2.axvline(x=avg_silhouette, color='red', linestyle='--')
                ax2.set_title('轮廓系数分析')
                ax2.set_xlabel('轮廓系数')
                ax2.set_ylabel('聚类标签')
            except Exception as e:
                print(f"计算轮廓系数时发生错误: {str(e)}")
                return plot_error_figure(save_dir, request_id,error_msg=str(e))
        else:
            # 绘制饼图显示各簇的样本分布
            cluster_sizes = pd.Series(y_pred).value_counts().sort_index()
            colors = plt.cm.viridis(np.linspace(0, 1, len(cluster_sizes)))
            
            ax2.pie(cluster_sizes, labels=[f'簇 {i}\n({size}个样本)' 
                    for i, size in enumerate(cluster_sizes)],
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90)
            ax2.set_title('聚类样本分布')

        plt.tight_layout()
        # 修改保存路径逻辑
        save_path = os.path.join(save_dir, f'{request_id}_clustering_eval.png')
        plt.savefig(save_path,bbox_inches='tight', dpi=150)
        plt.close()
        
        print(f"聚类可视化图像已保存到: {save_path}")
        return save_path
    except Exception as e:
        print(f"保存聚类评估图表时发生错误: {str(e)}")
        return plot_error_figure(save_dir, request_id,error_msg=str(e))
#------------------------------------绘图失败提示图------------------------------------
def plot_error_figure(save_dir, request_id,error_msg="绘图失败"):
    """
    绘制绘图失败提示图
    """
    plt.figure(figsize=(15, 5))
    for i in range(2):
        plt.subplot(1, 2, i+1)
        plt.text(0.5, 0.5, error_msg, 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=12)
        plt.axis('off')
    
    # 保存错误示图
    save_path = os.path.join(save_dir, f'{request_id}_plot_error.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.close()
    return save_path


#------------------------------------训练过程图表------------------------------------

def plot_training_process(model_info, train_results, save_dir, request_id):
    """
    绘制模型训练过程的图表,包含模型评估结果和训练进度
    params:
        - model_info: 模型信息字典
        - train_results: 训练结果字典 
        - save_dir: 保存目录
        - request_id: 请求ID
    return:
        - str: 图像保存路径
    """
    
    try:
        # 检查必要的参数
        if not train_results or not model_info:
            raise ValueError("训练结果或模型信息不能为空")
        # 设置中文字体和字体大小
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 13
        plt.rcParams['axes.titlesize'] = 13
        plt.rcParams['axes.labelsize'] = 13
        plt.rcParams['xtick.labelsize'] = 13
        plt.rcParams['ytick.labelsize'] = 13
        plt.rcParams['legend.fontsize'] = 13

        # 修改这部分代码来安全处理可能的元组值
        def safe_max(value, default=0):
            if isinstance(value, (int, float)):
                return max(0, value)
            elif isinstance(value, (tuple, list)):
                return max(0, value[0] if len(value) > 0 else default)
            return default

        # 将负值转换为0
        train_score = safe_max(train_results.get('train_score', 0))
        test_score = safe_max(train_results.get('test_score', 0))
        
        # 处理metrics中的负值
        metrics = train_results.get('metrics', {})
        if isinstance(metrics, dict):
            for key in metrics:
                if isinstance(metrics[key], (int, float, tuple, list)):
                    metrics[key] = safe_max(metrics[key])
        
        # 其他数值也确保非负
        metrics_data = {
            '训练时间(秒)': safe_max(train_results.get('time_elapsed', 0)),
            '模型大小(KB)': safe_max(train_results.get('model_size', 0)/1024)
        }
        # 设置子图数量和布局
        n_plots = 2 if train_results.get('metrics') else 1
        print(f"n_plots: {n_plots}")
        # 修改图像尺寸和布局设置
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        if n_plots == 1:
            axes = [axes]
            
        # 合并所有指标到一个横向柱状图
        metrics_data['训练得分'] = train_score
        metrics_data['测试得分'] = test_score
        x_pos = np.arange(len(metrics_data))
        axes[0].bar(x_pos, list(metrics_data.values()))
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels(list(metrics_data.keys()))
        axes[0].set_title('模型训练指标')
        # 添加数值标签
        for i, v in enumerate(metrics_data.values()):
            axes[0].text(i, v, f'{v:.2f}', ha='center', va='bottom')
        # 旋转x轴标签以防重叠
        plt.setp(axes[0].get_xticklabels(), rotation=30, ha='right')

        # 如果有评估矩阵数据,绘制评估指标对比图
        if train_results.get('metrics'):
            metrics = train_results['metrics']
            # 根据模型类型处理不同的评估指标
            if isinstance(metrics, dict) and ('train' in metrics or 'test' in metrics):
                # 有监督学习模型(分类/回归)
                train_metrics = metrics.get('train', {})
                test_metrics = metrics.get('test', {})
                
                metric_names = list(train_metrics.keys())
                train_values = [train_metrics[m] for m in metric_names]
                test_values = [test_metrics[m] for m in metric_names]
                
                x = np.arange(len(metric_names))
                width = 0.35
                
                axes[1].bar(x - width/2, train_values, width, label='训练集')
                axes[1].bar(x + width/2, test_values, width, label='测试集')
                
                axes[1].set_ylabel('得分')
                axes[1].set_title('评估指标对比')
                axes[1].set_xticks(x)
                axes[1].set_xticklabels(metric_names)
                axes[1].legend()
                
                plt.setp(axes[1].get_xticklabels(), rotation=30, ha='right')
                axes[1].tick_params(axis='x', labelsize=13)
                
                # 添加数值标签
                for i, v in enumerate(train_values):
                    axes[1].text(x[i] - width/2, v, f'{v:.2f}', ha='center', va='bottom')
                for i, v in enumerate(test_values):
                    axes[1].text(x[i] + width/2, v, f'{v:.2f}', ha='center', va='bottom')
                    
            else:
                # 无监督学习模型(聚类)
                metric_names = list(metrics.keys())
                metric_values = [metrics[m] for m in metric_names]
                
                x = np.arange(len(metric_names))
                axes[1].bar(x, metric_values)
                
                axes[1].set_ylabel('得分')
                axes[1].set_title('聚类评估指标')
                axes[1].set_xticks(x)
                axes[1].set_xticklabels(metric_names)
                
                plt.setp(axes[1].get_xticklabels(), rotation=30, ha='right')
                axes[1].tick_params(axis='x', labelsize=14)
                
                # 添加数值标签
                for i, v in enumerate(metric_values):
                    if v is not None:
                        axes[1].text(i, v, f'{v:.2f}', ha='center', va='bottom',fontsize=14)

             
        # 保存图像
        save_path = os.path.join(save_dir, f'{request_id}_train_process.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"训练过程图表已保存到: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"绘制训练过程图表时发生错误: {str(e)}")
        return plot_error_figure(save_dir, request_id,error_msg=str(e))



