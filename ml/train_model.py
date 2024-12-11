import pandas as pd
import os
import joblib
import time
import uuid
from tinydb import TinyDB, Query
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.decomposition import PCA
import numpy as np
from db.tiny_db import TinyDBUtil
from ml.model_status import log_progress
from ml.model_plot import plot_training_process
from sklearn.metrics import (
    precision_score, recall_score, f1_score,  # 分类指标
    mean_squared_error, mean_absolute_error, r2_score,  # 回归指标
    silhouette_score, calinski_harabasz_score, davies_bouldin_score  # 聚类指标
)
import re


def feature_engineering(df,feature_engineering_save_path,request_id, target_column=None):
    """
    修复：
    1. 增加目标列为空的判断
    2. 根据是否有目标列调整特征工程策略
    3. 优化异常处理
    4. 特征工程结果保存在文件中
    5. 增加特征重要性排序
    """
    df = df.copy()
    feature_engineering_info = {}    
    try:
        # 记录原始特征数量
        original_features_count = df.shape[1]
        # 检查输入数据
        if df is None or df.empty:
            raise ValueError("输入数据框为空")
            
        # 检查目标列
        if target_column!="" and target_column not in df.columns:
            raise ValueError(f"目标列 {target_column} 不存在于数据集中")
        print(f"目标列: {target_column}")
        print(f"数据集: {df.columns}")
        supervised = target_column!="" and target_column in df.columns
        # 保存目标列的值
        target_values = None
        if target_column in df.columns:
            target_values = df[target_column].copy()

        # 1. 数值特征标准化
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        if target_column and supervised:
            if target_column in numerical_columns:
                numerical_columns = numerical_columns.drop(target_column)

        if len(numerical_columns) > 0:
            scaler = StandardScaler()
            df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

        # 2. 对所有分类特征进行独热编码转换为数值
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            df = pd.get_dummies(df, columns=categorical_columns)

        # 3. 特征交互：仅在有监督学习且特征数量合理时生成(会增大特征维度)
        if supervised  and len(numerical_columns) > 0 and len(numerical_columns) <= 10:
            
            
            poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
            poly_features = poly.fit_transform(df[numerical_columns])
            poly_columns = poly.get_feature_names_out(numerical_columns)
            df_poly = pd.DataFrame(poly_features, columns=poly_columns)
            
            df = pd.concat([df, df_poly], axis=1)
            if target_column not in df.columns and target_values is not None:
                df[target_column] = target_values

        # 4. 降维：根据任务类型调整PCA策略(特征数大于30时进行降维)
        if df.shape[1] > 50:
            pca_info = {}
            # 无监督学习时保留更多维度(20)
            n_components = min(df.shape[1], 30 if not supervised else 20)
            pca = PCA(n_components=n_components)
            pca_features = pca.fit_transform(df)
            
            # 获取特征名称列表
            feature_names = df.columns.tolist()
            
            # 计算每个原始特征的重要性得分
            feature_importance = np.abs(pca.components_).sum(axis=0)
            feature_importance = feature_importance / feature_importance.sum()
            
            # 将特征名称和重要性得分组合
            feature_importance_pairs = list(zip(feature_names, feature_importance))
            sorted_features = sorted(feature_importance_pairs, key=lambda x: x[1], reverse=True)
            
            pca_info.update({
                'n_samples': pca_features.shape[0],
                'n_components': pca_features.shape[1], #降维后特征数量
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'cumulative_variance_ratio': np.cumsum(pca.explained_variance_ratio_).tolist(),
                'feature_names': [f'PC{i+1}' for i in range(n_components)],
                'important_features': [
                    {'name': name, 'importance': float(score)} 
                    for name, score in sorted_features[:10]  # 只保留前10个重要特征
                ],
                'is_supervised': supervised
            })
            
            # 如果需要保存完整的转换后数据，建议写入文件而不是存在内存中
            if feature_engineering_save_path:  # 确保有输出路径
                os.makedirs(feature_engineering_save_path, exist_ok=True)
                pca_output_path = os.path.join(feature_engineering_save_path, f"{request_id}-pca_features.npy")
                np.save(pca_output_path, pca_features)
                pca_info['pca_features_path'] = pca_output_path
            feature_engineering_info.update({
                'pca_info': pca_info
            })
        # 检查特征数量变化
        final_features_count = df.shape[1]
        print(f"特征工程前后特征数量变化: {original_features_count} -> {final_features_count}")
        if feature_engineering_save_path:
            #保存特征工程后数据
            os.makedirs(feature_engineering_save_path, exist_ok=True)
            feature_engineering_output_path = os.path.join(feature_engineering_save_path, f"{request_id}-features.npy")
            np.save(feature_engineering_output_path, df)
            feature_engineering_info['feature_engineering_path'] = feature_engineering_output_path
        return df, feature_engineering_info
        
    except Exception as e:
        print(f"特征工程过程中发生错误: {str(e)}")
        raise  
        

def train_and_save_model(request_id, source_file_hash, output_dir_path, df, target_column, callback=None):
    """修复模型训练和保存过程"""
    try:
        # 记录总体开始时间
        start_time = time.time()
        
        # 在函数开始处添加 CPU 核心数设置
        os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 1)  # 设置最大CPU核心数
        
        # 验证输入参数
        if not request_id or not source_file_hash or not output_dir_path:
            raise ValueError("必需的参数不能为空")
            
        if df is None or df.empty:
            raise ValueError("输入数据框不能为空")
            
        # 记录模型信息
        model_info = {
            "request_id": request_id,
            "source_file_hash": source_file_hash,
            "output_dir_path": output_dir_path, 
            "target_column": target_column,
            "model_name": None, #模型名称
            "test_size": None, #测试集比例
            "model_save_path": None, #模型保存路径
            "created_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), #创建时间
            "model_data_type": 1, #模型数据类型(1:流量(数据集)、2:情报(文本))
            "model_type": 1, #模型类型(1:分类模型、2:回归模型、3:聚类模型、4:NLP模型)
            "model_algorithm": None, #模型算法
            "model_framework": "scikit-learn", #训练框架
            "features": [], #特征列表
            'feature_count': len(df.columns),  # 添加特征数量
            'rows_count': len(df),  # 添加数据行数
            "model_size": 0, #模型大小(B)
        }
        train_results = {
            'train_score': 0, #训练得分
            'test_score': 0, #测试得分
            'metrics': {},#评估指标
            'model_size': 0, #模型大小(B)
            'feature_count': len(df.columns),  # 添加特征数量
            'rows_count': len(df),  # 添加数据行数
            'time_elapsed': 0,
            'model_algorithm': '', #模型算法
        }
        # 添加数据验证
        df = df.copy()  # 创建副本避免修改原始数据
        df = df.dropna()  # 处理空值
        
        if target_column and target_column not in df.columns:
            raise ValueError(f"目标列 {target_column} 不存在于数据集中")
        # 记录训练开始时间
        start_time = time.time()

        # 1. 特征工程
        try:
            print('开始特征工程...')
            log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering started")
            feature_engineering_df, feature_engineering_info = feature_engineering(df, output_dir_path+'/feature_engineering', request_id, target_column)  # 特征工程步骤
            print(f"特征工程后df: {feature_engineering_df.columns}")
            model_info.update({
                'feature_engineering_info': feature_engineering_info
            })
            print('特征工程完成！')
            log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering completed")
        except Exception as e:
            print(f"特征工程过程中发生错误: {str(e)}")
            log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering failed", error=str(e))
            raise

    

        # 3. 划分特征和标签
        if target_column:
            if target_column not in feature_engineering_df.columns:
                raise ValueError(f"目标列 {target_column} 不存在于数据集中")
            y = feature_engineering_df[target_column]
            X = feature_engineering_df.drop(columns=[target_column])
            model_info["target_column"] = target_column
            print("开始划分训练集和测试集...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            log_progress(request_id, source_file_hash,"Train/Test Split", "Train/test split completed")  # 记录进度
            model_info["test_size"] = 0.2
        else:
            # 无监督学习,不需要标签
            X = feature_engineering_df
            X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
            y_train = y_test = None
            log_progress(request_id, source_file_hash,"Train/Test Split", "Train/test split completed (unsupervised)")
            model_info["test_size"] = 0.2

        # 4. 根据特征选择合适的模型
        def select_model_callback(info):
            callback(request_id, source_file_hash,{
                'model_select_info': info
            })
        model,model_select_info = select_model_based_on_features(feature_engineering_df, target_column,select_model_callback)
        model_name = model.__class__.__name__
        model_info["model_name"] = model_name
        model_info["model_algorithm"] = model_select_info.get('model_algorithm')
        model_info["model_framework"] = model_select_info.get('model_framework')
        model_info["model_type"] = model_select_info.get('model_type')
        train_results['model_algorithm'] = model_info['model_algorithm']
        # 记录开始训练的时间
        log_progress(request_id,source_file_hash, "Model Training", "Training started")

        # 5. 训练模型
        model_start_time = time.time()
        if hasattr(model, 'supports_iterative_training') and model.supports_iterative_training:
            # 对于支持迭代训练的模型
            if model_name == 'RandomForestClassifier' or model_name == 'RandomForestRegressor':
                n_estimators_per_iter = 10  # 每次迭代训练10个树
                total_estimators = model.n_estimators
                current_estimators = 0
                
                while current_estimators < total_estimators:
                    current_estimators += n_estimators_per_iter
                    model.set_params(n_estimators=min(current_estimators, total_estimators))
                    model.fit(X_train, y_train)
            else:
                # 非随机森林模型直接训练
                model.fit(X_train, y_train)
                
            if callback:
                train_score = model.score(X_train, y_train)
                test_score = model.score(X_test, y_test)
                train_results['train_score'] = train_score
                train_results['test_score'] = test_score
                
                # 使用新的calculate_metrics函数获取评估指标
                metrics = calculate_metrics(model, X_train, X_test, y_train, y_test, model_info["model_type"])
                train_results['metrics'] = metrics
                
                callback(request_id, source_file_hash, {
                    'model_select_info': model_select_info,
                    'train_progress_info': {
                        'progress': 100,
                        'train_score': train_score,
                        'test_score': test_score,
                        'time_elapsed': time.time() - model_start_time,
                        'metrics': metrics
                    }
                })
        else:
            # 对于不支持迭代训练的模型
            model.fit(X_train, y_train)
            if callback:
                # 检查是否为聚类模型（特别是DBSCAN）
                if model_info["model_type"] == 3:  # 聚类模型
                    # 聚类模型不使用传统的score，而是使用专门的聚类评估指标
                    metrics = calculate_metrics(model, X_train, X_test, y_train, y_test, model_info["model_type"])
                    train_results['train_score'] = metrics.get('silhouette', 0)  # 使用轮廓系数作为得分
                    train_results['test_score'] = metrics.get('silhouette', 0)
                    train_results['metrics'] = metrics
                else:
                    # 对于其他模型保持原有的评分方式
                    train_score = model.score(X_train, y_train)
                    test_score = model.score(X_test, y_test)
                    train_results['train_score'] = train_score
                    train_results['test_score'] = test_score
                    metrics = calculate_metrics(model, X_train, X_test, y_train, y_test, model_info["model_type"])
                    train_results['metrics'] = metrics

                callback(request_id, source_file_hash, {
                    'model_select_info': model_select_info,
                    'train_progress_info': {
                        'progress': 100,
                        'train_score': train_results['train_score'],
                        'test_score': train_results['test_score'],
                        'time_elapsed': time.time() - model_start_time,
                        'metrics': metrics
                    }
                })

        log_progress(request_id,source_file_hash, "Model Training", "Training completed")
        # 6. 保存模型
        save_dir = output_dir_path+'/save'
        os.makedirs(save_dir, exist_ok=True)
        model_save_path = os.path.join(save_dir, f"{request_id}-{model_name}.joblib")
        joblib.dump(model, model_save_path)
        model_info["model_save_path"] = model_save_path
        log_progress(request_id,source_file_hash, "Model Saving", f"Model save success")
        train_time = round(time.time() - model_start_time, 3),#训练时间(秒)
        # 在模型训练完成后更新模型记录信息
        model_info.update({
            'training_time': train_time,
            "model_size": os.path.getsize(model_save_path)  # 记录模型文件大小
        })
        train_results['time_elapsed'] = train_time
        train_results['model_size'] = model_info['model_size']
        # 在模型训练完成后，绘制训练过程图像
        train_results_image_path = plot_training_process(
            model_info=model_info,
            train_results=train_results,
            save_dir=save_dir,
            request_id=request_id
        )
        if train_results_image_path!=None:
            model_info.update({
                'train_results': {
                    'visualization_path': train_results_image_path
                }
            })
        
        # 在训练完成后更新训练用时
        train_results['time_elapsed'] = round(time.time() - start_time, 3)  # 记录总训练用时(秒)
        
        # 在回调中也更新训练用时
        if callback:
            callback(request_id, source_file_hash, {
                'model_select_info': model_select_info,
                'train_progress_info': {
                    'progress': 100,
                    'time_elapsed': train_results['time_elapsed'],
                    **train_results
                }
            })

        return feature_engineering_df,model_info, model_save_path
        
    except Exception as e:
        log_progress(request_id, source_file_hash,
                     stage="Model Training",
                     message="Error",
                     error=f"训练失败: {str(e)}")
        raise



def select_model_based_on_features(df, target_column=None, callback=None):
    """添加回调参数和错误处理"""
    try:
        if df is None or df.empty:
            raise ValueError("输入数据不能为空")           
        
        # 如果目标列为空或者为空字符串,则选择无监督模型
        if target_column is None or target_column == "" or target_column not in df.columns:
            model, model_select_info = select_unsupervised_model(df)
        else:
            model, model_select_info = select_supervised_model(df, target_column)
            
        print(f"选择模型: {model.__class__.__name__}")
        
        model_type_name_map = {
            'classification': 1,
            'regression': 2,
            'clustering': 3,
            'nlp': 4
        }
        model_type = model_type_name_map.get(model_select_info.get('task_type'),0)
        model_select_info['model_type'] = model_type
        # 确保返回值
        return model, model_select_info
        
    except Exception as e:
        print(f"模型选择过程中发生错误: {str(e)}")
        raise

def select_supervised_model(df, target_column):
    """
    选择有监督学习模型
    """
    # 获取目标列的数据类型和基本信息
    target_dtype = df[target_column].dtype
    n_samples, n_features = df.shape
    numeric_features = df.select_dtypes(include=[np.number]).columns
    categorical_features = df.select_dtypes(exclude=[np.number]).columns
    
    # 确定任务类型
    if target_dtype in [np.float64, np.int64]:
        n_unique_values = df[target_column].nunique()
        task_type = 'classification' if n_unique_values <= 10 else 'regression'
    else:
        task_type = 'classification'
    
    # 根据任务类型选择模型
    if task_type == 'classification':
        model, model_select_info = select_classification_model(df, target_column, n_samples, 
                                                            n_features, numeric_features, 
                                                            categorical_features)
    else:
        model, model_select_info = select_regression_model(n_samples, n_features)
    
    return model, model_select_info

def select_unsupervised_model(df):
    """
    选择无监督学习模型
    """
    from sklearn.cluster import KMeans, DBSCAN
    n_samples = len(df)
    if n_samples < 1000:
        model = KMeans(n_clusters=5)  # 小数据集使用K-means
        n_clusters = 5
    else:
        model = DBSCAN(eps=0.3, min_samples=10)  # 大数据集使用DBSCAN
        # DBSCAN不需要预先指定簇的数量,在训练后获取
        n_clusters = None

    model_select_info = {
        'task_type': 'clustering',
        'n_samples': n_samples,
        'n_clusters': n_clusters if isinstance(model, KMeans) else None,
        'n_features': df.shape[1],
        'model_algorithm': model.__class__.__name__,
        'model_framework': 'scikit-learn'
    }  

    model.supports_iterative_training = False
    return model, model_select_info

def select_classification_model(df, target_column, n_samples, n_features, 
                              numeric_features, categorical_features):
    """
    选择分类模型
    """
    n_classes = df[target_column].nunique()
    
    if n_samples < 1000:
        model = LogisticRegression(max_iter=1000, warm_start=True, solver='lbfgs')
    elif len(categorical_features) > len(numeric_features):
        # 修改 RandomForestClassifier 的并行设置
        n_jobs = min(4, os.cpu_count() or 1)  # 限制最大并行数
        model = RandomForestClassifier(n_estimators=100, warm_start=True, n_jobs=n_jobs)
    else:
        if n_samples > 10000:
            model = SVC(kernel='rbf', probability=True, cache_size=2000)
        else:
            model = SVC(kernel='rbf', probability=True)
    
    model.supports_iterative_training = isinstance(model, (RandomForestClassifier, LogisticRegression))
    
    model_select_info = {
        'task_type': 'classification',
        'n_samples': n_samples,
        'n_features': n_features,
        'numeric_features': len(numeric_features),
        'categorical_features': len(categorical_features),
        'n_classes': n_classes,
        'model_algorithm': model.__class__.__name__,
        'model_framework': 'scikit-learn'
    }
    
    return model, model_select_info

def select_regression_model(n_samples, n_features):
    """
    选择回归模型
    """
    if n_samples < 1000:
        model = LinearRegression()
    elif n_features > 10:
        model = RandomForestRegressor(n_estimators=100, warm_start=True, n_jobs=-1)
    else:
        model = SVR(kernel='rbf')
    
    model.supports_iterative_training = isinstance(model, RandomForestRegressor)
    
    model_select_info = {
        'task_type': 'regression',
        'n_samples': n_samples,
        'n_features': n_features,
        'model_algorithm': model.__class__.__name__,
        'model_framework': 'scikit-learn'
    }
    
    return model, model_select_info

def calculate_metrics(model, X_train, X_test, y_train, y_test, model_type):
    """计算不同类型模型的评估指标"""
    metrics = {}
    
    if model_type == 1:  # 分类模型
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        metrics = {
            'train': {
                'precision': precision_score(y_train, y_pred_train, average='weighted'),
                'recall': recall_score(y_train, y_pred_train, average='weighted'),
                'f1': f1_score(y_train, y_pred_train, average='weighted')
            },
            'test': {
                'precision': precision_score(y_test, y_pred_test, average='weighted'),
                'recall': recall_score(y_test, y_pred_test, average='weighted'),
                'f1': f1_score(y_test, y_pred_test, average='weighted')
            }
        }
        
    elif model_type == 2:  # 回归模型
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        metrics = {
            'train': {
                'mse': mean_squared_error(y_train, y_pred_train),
                'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'mae': mean_absolute_error(y_train, y_pred_train),
                'r2': r2_score(y_train, y_pred_train)
            },
            'test': {
                'mse': mean_squared_error(y_test, y_pred_test),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'mae': mean_absolute_error(y_test, y_pred_test),
                'r2': r2_score(y_test, y_pred_test)
            }
        }
        
    elif model_type == 3:  # 聚类模型
        # 对于聚类模型,我们只需要特征数据
        labels_train = model.labels_
        
        metrics = {
            'silhouette': silhouette_score(X_train, labels_train),
            'calinski_harabasz': calinski_harabasz_score(X_train, labels_train),
            'davies_bouldin': davies_bouldin_score(X_train, labels_train),
            'inertia': model.inertia_ if hasattr(model, 'inertia_') else None
        }
    
    return metrics

