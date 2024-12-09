import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error, 
    mean_absolute_error,
    r2_score,
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    silhouette_score
)
from ml.train_model import feature_engineering
from ml.model_plot import save_regression_plot, save_classification_plot,save_clustering_plot
import os

def evaluate_model(request_id, model_path, df, target_column, model_info):
    """主评估函数"""
    try:
        df = df.copy()
        # 1.加载模型
        model = joblib.load(model_path)
        # 2.从 model_info 获取模型类型
        model_type = model_info.get('model_type', 0)  # 1:分类模型、2:回归模型、3:聚类模型
        print(f"模型类型: {model_type}")
        
        # # 3.特征工程(从model_info中获取)
        #df, pca_info = feature_engineering(df, target_column)
        print("model_info:",model_info)
        # 4.判断是否使用PCA特征
        pca_info = model_info.get('pca_info', None)
        pca_info = None
        if pca_info and pca_info.get('pca_features_path') is not None:
            #读取降维后的数据   
            print("使用PCA特征进行评估")
            evaluation_data = np.load(pca_info['pca_features_path'])
        else:
            print("使用原始特征进行评估")
            evaluation_data = df
       
        # 5.获取保存路径(评估图像)
        save_dir = os.path.join(os.path.dirname(model_path), 'visualizations')
        os.makedirs(save_dir, exist_ok=True)
        evaluation_results = {}
        
        # 6.根据模型类型选择评估方法
        if model_type in [1, 2]:  # 有监督学习（分类或回归）
            if not target_column or target_column not in df.columns:
                raise ValueError(f"有监督学习需要有效的目标列。当前目标列 '{target_column}' 无效")
                
            X = evaluation_data if isinstance(evaluation_data, np.ndarray) else evaluation_data.drop(columns=[target_column])
            y = df[target_column]
            
            # 划分测试集
            _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            y_pred = model.predict(X_test)
            
            if model_type == 2:  # 回归模型
                evaluation_results = evaluate_regression_model(y_test, y_pred)
                visualization_path = save_regression_plot(y_test, y_pred, save_dir, request_id)
                evaluation_results['visualization_path'] = visualization_path
            else:  # 分类模型
                evaluation_results = evaluate_classification_model(y_test, y_pred)
                visualization_path = save_classification_plot(y_test, y_pred, save_dir, request_id)
                evaluation_results['visualization_path'] = visualization_path
                
        elif model_type == 3:  # 聚类模型
            if pca_info and 'pca_features' in pca_info:
                evaluation_results = evaluate_clustering_with_pca(
                    pca_features=evaluation_data,
                    pca_info=pca_info,
                    model=model,
                    save_dir=save_dir,
                    request_id=request_id
                )
            else:
                evaluation_results = evaluate_clustering_model(
                    model=model, 
                    X=evaluation_data, 
                    model_info=model_info, 
                    save_dir=save_dir,
                    request_id=request_id
                )
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        return evaluation_results
                
    except Exception as e:
        print(f"模型评估过程中发生错误: {str(e)}")
        raise

def evaluate_regression_model(y_test, y_pred):
    """评估回归模型性能"""
    return {
        'MSE': float(mean_squared_error(y_test, y_pred)),
        'RMSE': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'MAE': float(mean_absolute_error(y_test, y_pred)),
        'R2': float(r2_score(y_test, y_pred))
    }

def evaluate_classification_model(y_test, y_pred):
    """评估分类模型性能"""
    return {
        'Accuracy': float(accuracy_score(y_test, y_pred)),
        'Precision': float(precision_score(y_test, y_pred, average='weighted')),
        'Recall': float(recall_score(y_test, y_pred, average='weighted')),
        'F1-Score': float(f1_score(y_test, y_pred, average='weighted'))
    }

def evaluate_clustering_model(model, X, model_info, save_dir, request_id):
    """评估聚类模型性能"""
    try:
        print(f"聚类评估输入数据形状: {X.shape}")
        print(f"聚类评估输入列: {X.columns.tolist() if isinstance(X, pd.DataFrame) else 'numpy array'}")
        
        # 确保数据是数值类型
        if isinstance(X, pd.DataFrame):
            X = X.select_dtypes(include=[np.number])
            if X.empty:
                raise ValueError("数据框中没有数值类型的列")
        
        # 检查特征数量是否匹配
        n_features_model = model.n_features_in_ if hasattr(model, 'n_features_in_') else None
        n_features_data = X.shape[1]
        
        if n_features_model and n_features_data != n_features_model:
            print(f"警告：模型期望 {n_features_model} 个特征，但输入数据有 {n_features_data} 个特征")
            # 如果是DataFrame，调整特征数量
            if isinstance(X, pd.DataFrame):
                if n_features_data > n_features_model:
                    X = X.iloc[:, :n_features_model]
                else:
                    raise ValueError(f"输入特征数量不足：需要 {n_features_model} 个，但只有 {n_features_data} 个")
        
        results = {}
        
        # 获取聚类预测
        y_pred = model.predict(X)
        
        # 计算轮廓系数
        try:
            if len(np.unique(y_pred)) > 1:  # 确保有多个簇
                silhouette_avg = silhouette_score(X, y_pred)
                results['Silhouette Score'] = float(silhouette_avg)
            else:
                print("无法计算轮廓系数: 只有一个簇")
                results['Silhouette Score'] = None
        except Exception as e:
            print(f"无法计算轮廓系数: {str(e)}")
            results['Silhouette Score'] = None
        
        # 如果是KMeans模型，添加惯性
        if hasattr(model, 'inertia_'):
            results['Inertia'] = float(model.inertia_)
        
        # 生成聚类可视化
        try:
            visualization_path = save_clustering_plot(X, y_pred, save_dir, request_id)
            results['visualization_path'] = visualization_path
        except Exception as e:
            print(f"生成聚类可视化时发生错误: {str(e)}")
        
        return results
        
    except Exception as e:
        print(f"聚类评估过程中发生错误: {str(e)}")
        raise

def evaluate_clustering_with_pca(pca_features, pca_info, model, save_dir, request_id):
    """
        使用PCA特征评估聚类模型性能
        params:
            - pca_features: PCA特征(X降维后)
            - pca_info: PCA信息
            - model: 聚类模型
            - save_dir: 保存目录
            - request_id: 请求ID
    """
    evaluation_results = {}
    
    print(f"使用PCA转换后的特征进行聚类评估 "
          f"(解释方差比例: {sum(pca_info['explained_variance_ratio']):.2%})")
    
    # 更新PCA相关评估结果
    evaluation_results.update({
        'pca_explained_variance': pca_info['explained_variance_ratio'],
        'cumulative_variance_ratio': pca_info['cumulative_variance_ratio'],
        'n_components': pca_info['n_components'],
        'n_samples': pca_info['n_samples'],
        'important_features': pca_info['important_features']
    })
    
    # 获取聚类预测
    y_pred = model.predict(pca_features)
    
    try:
        # 计算每个簇的统计信息
        cluster_stats = {}
        for cluster_id in np.unique(y_pred):
            cluster_features = pca_features[y_pred == cluster_id]
            # 计算前3个主成分的统计信息
            stats = {}
            for i in range(min(3, pca_features.shape[1])):
                pc_name = f'PC{i+1}'
                stats[pc_name] = {
                    'mean': float(np.mean(cluster_features[:,i])),
                    'std': float(np.std(cluster_features[:,i])),
                }
            cluster_stats[f'cluster_{cluster_id}'] = {
                'stats': stats,
                'size': int(len(cluster_features)),
                'percentage': float(len(cluster_features) / len(pca_features))
            }
        evaluation_results['cluster_stats'] = cluster_stats
        
        # 计算轮廓系数
        silhouette_avg = silhouette_score(pca_features, y_pred)
        evaluation_results['silhouette_score'] = float(silhouette_avg)
        
    except Exception as e:
        print(f"计算聚类统计信息时发生错误: {str(e)}")
    
    # 生成聚类可视化
    try:
        visualization_path = save_clustering_plot(pca_features, y_pred, save_dir, request_id)
        evaluation_results['visualization_path'] = visualization_path
    except Exception as e:
        print(f"生成聚类可视化时发生错误: {str(e)}")
        
    return evaluation_results

