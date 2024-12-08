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
        
        # 1. 混淆矩阵热力图
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
        ax1.set_title('混淆矩阵')
        ax1.set_xlabel('预测类别')
        ax1.set_ylabel('实际类别')
        
        # 2. 每个类别的准确率柱状图
        class_accuracy = cm.diagonal() / cm.sum(axis=1)
        classes = np.unique(y_test)
        ax2.bar(classes, class_accuracy)
        ax2.set_title('各类别准确率')
        ax2.set_xlabel('类别')
        ax2.set_ylabel('准确率')
        ax2.set_ylim(0, 1)  # 设置y轴范围为0-1
        
        # 3. 预测分布与实际分布对比柱状图
        width = 0.35
        pred_counts = pd.Series(y_pred).value_counts()
        true_counts = pd.Series(y_test).value_counts()
        
        x = np.arange(len(classes))
        ax3.bar(x - width/2, true_counts, width, label='实际分布', alpha=0.8)
        ax3.bar(x + width/2, pred_counts, width, label='预测分布', alpha=0.8)
        
        ax3.set_xticks(x)
        ax3.set_xticklabels(classes)
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
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建1行3列的子图
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
        
        # 第一个子图: 原始特征空间
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
            return None

        ax1.set_title('原始特征空间聚类结果')
        ax1.set_xlabel(f'特征 {top_features[0]}')
        ax1.set_ylabel(f'特征 {top_features[1]}')
        plt.colorbar(scatter1, ax=ax1)
        
        # 第二个子图: PCA降维可视化
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        scatter2 = ax2.scatter(X_pca[:, 0], X_pca[:, 1], c=y_pred, cmap='viridis')
        ax2.set_title('PCA降维聚类结果')
        ax2.set_xlabel('第一主成分')
        ax2.set_ylabel('第二主成分')
        plt.colorbar(scatter2, ax=ax2)
        
        # 第三个子图: 轮廓系数可视化
        silhouette_vals = silhouette_samples(X, y_pred)
        n_clusters = len(np.unique(y_pred))
        y_lower, y_upper = 0, 0
        
        for i in range(n_clusters):
            cluster_silhouette_vals = silhouette_vals[y_pred == i]
            cluster_silhouette_vals.sort()
            y_upper += len(cluster_silhouette_vals)
            
            ax3.fill_betweenx(np.arange(y_lower, y_upper),
                             0, cluster_silhouette_vals,
                             alpha=0.7)
            y_lower += len(cluster_silhouette_vals)
        
        ax3.set_title('轮廓系数分析')
        ax3.set_xlabel('轮廓系数')
        ax3.set_ylabel('聚类标签')
        ax3.axvline(x=np.mean(silhouette_vals), color='red', linestyle='--')
        
        plt.tight_layout()
        
        # 修改保存路径逻辑
        save_path = os.path.join(save_dir, f'{request_id}_clustering_eval.png')
        plt.savefig(save_path)
        plt.close()
        
        print(f"聚类可视化图像已保存到: {save_path}")
        return save_path
    except Exception as e:
        print(f"保存聚类评估图表时发生错误: {str(e)}")
        return None


#------------------------------------训练过程图表------------------------------------
def plot_training_process(model_info, save_dir, request_id):
    """
    绘制模型训练过程的图表，包含模型评估结果和训练进度
    params:
        - model_info: 模型信息字典
        - save_dir: 保存目录
        - request_id: 请求ID
    return:
        - str: 图像保存路径
    """
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建2行1列的子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # 1. 绘制评估指标柱状图
        evaluation_results = model_info.get('evaluation_results', {})
        if evaluation_results:
            metrics = []
            values = []
            for metric, value in evaluation_results.items():
                if isinstance(value, (int, float)):  # 只使用数值型指标
                    metrics.append(metric)
                    values.append(value)
            
            if metrics:
                bars = ax1.bar(metrics, values)
                ax1.set_title('模型评估指标')
                ax1.set_ylim(0, 1.1)  # 假设指标值在0-1之间
                ax1.grid(True, axis='y')
                
                # 在柱状图上添加具体数值
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.3f}',
                            ha='center', va='bottom')
        
        # 2. 绘制训练进度和时间信息
        train_info = model_info.get('train_progress_info', {})
        if train_info:
            # 获取关键信息
            progress = train_info.get('progress', 0)
            time_elapsed = train_info.get('time_elapsed', 0)
            train_score = train_info.get('train_score', 0)
            test_score = train_info.get('test_score', 0)
            
            # 创建训练信息表格
            table_data = [
                ['训练进度', f'{progress:.1f}%'],
                ['已用时间', f'{time_elapsed:.1f}秒'],
                ['训练集得分', f'{train_score:.3f}'],
                ['测试集得分', f'{test_score:.3f}']
            ]
            
            # 隐藏坐标轴
            ax2.axis('off')
            
            # 创建表格
            table = ax2.table(cellText=table_data,
                            colWidths=[0.3, 0.3],
                            cellLoc='center',
                            loc='center',
                            bbox=[0.2, 0.2, 0.6, 0.6])  # 调整表格位置和大小
            
            # 设置表格样式
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1.5, 2)
            
            # 设置标题
            ax2.set_title('训练进度信息', pad=20)
        
        plt.tight_layout()
        
        # 修改保存路径生成逻辑
        save_path = os.path.join(save_dir, f'{request_id}_train_process.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        return save_path
    except Exception as e:
        print(f"绘制训练过程图表时发生错误: {str(e)}")
        return None
