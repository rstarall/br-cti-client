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
    
       
        # 5.获取保存路径(评估图像)
        save_dir = os.path.join(os.path.dirname(model_path), 'visualizations')
        os.makedirs(save_dir, exist_ok=True)
        evaluation_results = {}
        
        # 6.根据模型类型选择评估方法
        if model_type in [1, 2]:  # 有监督学习（分类或回归）
            if not target_column or target_column not in df.columns:
                raise ValueError(f"有监督学习需要有效的目标列。当前目标列 '{target_column}' 无效")
                
            X = df.drop(columns=[target_column])
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
            evaluation_results = evaluate_clustering_model(
                model=model, 
                X=df, 
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

def evaluate_clustering_model(model, X, save_dir, request_id):
    """评估聚类模型性能"""
    try:
        print(f"聚类评估输入数据形状: {X.shape}")
        print(f"聚类评估输入列: {X.columns.tolist() if isinstance(X, pd.DataFrame) else 'numpy array'}")
        
        # 对非数值列进行编码
        if isinstance(X, pd.DataFrame):
            le = LabelEncoder()
            for column in X.columns:
                if X[column].dtype == 'object':
                    X[column] = le.fit_transform(X[column].astype(str))
            
            # 确保所有列都转换为数值类型
            X = X.astype(float)
        
        # 检查特征数量是否匹配
        n_features_model = model.n_features_in_ if hasattr(model, 'n_features_in_') else None
        n_features_data = X.shape[1]
        
        if n_features_model and n_features_data != n_features_model:
            raise ValueError(f"输入特征数量不匹配：需要 {n_features_model} 个，但有 {n_features_data} 个")
        
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
                results['Silhouette Score'] = 0
        except Exception as e:
            print(f"无法计算轮廓系数: {str(e)}")
            results['Silhouette Score'] = 0
        
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

