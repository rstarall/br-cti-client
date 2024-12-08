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


def feature_engineering(df, model_info={}, target_column=None):
    """
    修复：
    1. 默认可变参数问题
    2. 添加空值检查
    3. 添加异常处理
    """
    if model_info is None:
        model_info = {}
    
    try:
        # 检查输入数据
        if df.empty:
            raise ValueError("输入数据框为空")
            
        # 1. 特征缩放：对数值特征进行标准化
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        if target_column and target_column in numerical_columns:
            numerical_columns = numerical_columns.drop(target_column)

        if len(numerical_columns) > 0:
            scaler = StandardScaler()
            df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

        # 2. 类别特征编码：对对象类型列进行独热编码
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            df = pd.get_dummies(df, columns=categorical_columns)

        # 3. 特征交互：仅在特征数量合理时生成多项式特征
        if len(numerical_columns) > 0 and len(numerical_columns) <= 10:  # 限制特征数量
            poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
            poly_features = poly.fit_transform(df[numerical_columns])
            poly_columns = poly.get_feature_names_out(numerical_columns)
            df_poly = pd.DataFrame(poly_features, columns=poly_columns)
            df = pd.concat([df, df_poly], axis=1)

        # 4. 降维：仅在特征数量较大时使用PCA
        if df.shape[1] > 10:
            n_components = min(10, df.shape[1] - 1)  # 动态调整组件数
            pca = PCA(n_components=n_components)
            pca_features = pca.fit_transform(df)
            model_info['pca'] = pca.explained_variance_ratio_.tolist()
            
        return df, model_info
        
    except Exception as e:
        print(f"特征工程过程中发生错误: {str(e)}")
        raise

def train_and_save_model(request_id, source_file_hash, output_dir_path, df, target_column, callback=None):
    """修复模型训练和保存过程"""
    try:
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
            "pca": None, #主成分信息
            "training_time": None, #训练时间
            "created_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), #创建时间
            "model_data_type": 1, #模型数据类型(1:流量(数据集)、2:情报(文本))
            "model_type": 1, #模型类型(1:分类模型、2:回归模型、3:聚类模型、4:NLP模型)
            "model_algorithm": None, #模型算法
            "model_framework": "scikit-learn", #训练框架
            "features": [], #特征列表
            "model_size": 0, #模型大小(B)
            "data_size": 0, #数据大小(B)
            "cti_id": "" #关联的情报ID
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
            df, model_info = feature_engineering(df, model_info, target_column)  # 特征工程步骤
            print('特征工程完成！')
            log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering completed")
        except Exception as e:
            print(f"特征工程过程中发生错误: {str(e)}")
            log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering failed", error=str(e))
            raise

        # 2. 编码类别型特征
        try:
            print("开始类别型特征编码...")
            log_progress(request_id, source_file_hash, "Label Encoding", "Label encoding started")
            for col in df.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
            log_progress(request_id, source_file_hash, "Label Encoding", "Label encoding completed")  # 记录进度
        except Exception as e:
            print(f"类别型特征编码过程中发生错误: {str(e)}")
            log_progress(request_id, source_file_hash, "Label Encoding", "Label encoding failed", error=str(e))
            raise

        # 3. 划分特征和标签
        if target_column:
            X = df.drop(columns=[target_column])
            y = df[target_column]
            model_info["target_column"] = target_column
            print("开始划分训练集和测试集...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            log_progress(request_id, source_file_hash,"Train/Test Split", "Train/test split completed")  # 记录进度
            model_info["test_size"] = 0.2
        else:
            # 无监督学习,不需要标签
            X = df
            X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
            y_train = y_test = None
            log_progress(request_id, source_file_hash,"Train/Test Split", "Train/test split completed (unsupervised)")
            model_info["test_size"] = 0.2

        # 4. 根据特征选择合适的模型
        def select_model_callback(info):
            callback(request_id, source_file_hash,{
                'model_select_info': info
            })
        model,model_select_info = select_model_based_on_features(df, target_column,select_model_callback)
        model_name = model.__class__.__name__
        model_info["model_name"] = model_name
        # 记录开始训练的时间
        log_progress(request_id,source_file_hash, "Model Training", "Training started")

        # 5. 训练模型
        model_start_time = time.time()
        
        if hasattr(model, 'supports_iterative_training') and model.supports_iterative_training:
            # 对于支持迭代训练的模型（随机森林）
            n_estimators_per_iter = 10  # 每次迭代训练10个树
            total_estimators = model.n_estimators
            current_estimators = 0
            
            while current_estimators < total_estimators:
                current_estimators += n_estimators_per_iter
                model.set_params(n_estimators=min(current_estimators, total_estimators))
                model.fit(X_train, y_train)
                
                if callback:
                    # 计算当前性能指标
                    progress = (current_estimators / total_estimators) * 100
                    train_score = model.score(X_train, y_train)
                    test_score = model.score(X_test, y_test)
                    
                    if hasattr(model, 'predict_proba'):
                        # 对于分类问题，可以获取概率预测
                        train_proba = model.predict_proba(X_train)
                        test_proba = model.predict_proba(X_test)
                        metrics = {
                            'train_proba': train_proba,
                            'test_proba': test_proba
                        }
                    else:
                        metrics = {}
                    
                    callback(request_id, source_file_hash, {
                        'model_select_info': model_select_info,
                        'train_progress_info': {
                            'progress': progress,
                            'current_iter': current_estimators,
                            'total_iter': total_estimators,
                            'train_score': train_score,
                            'test_score': test_score,
                            'time_elapsed': time.time() - model_start_time,
                            **metrics
                        }
                    })
        else:
            # 对于不支持迭代训练的模型
            model.fit(X_train, y_train)
            if callback:
                callback(request_id, source_file_hash, {
                    'model_select_info': model_select_info,
                    'train_progress_info': {
                        'progress': 100,
                        'train_score': model.score(X_train, y_train),
                        'test_score': model.score(X_test, y_test),
                        'time_elapsed': time.time() - model_start_time
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

        # 在模型训练完成后更新模型信息
        model_info.update({
            "model_algorithm": model.__class__.__name__,  # 记录具体使用的算法
            "model_type": 1 if model_select_info.get('task_type') == 'classification' else 2,  # 根据任务类型设置模型类型
            "model_size": os.path.getsize(model_save_path)  # 记录模型文件大小
        })

        # 在模型训练完成后，绘制训练过程图像
        train_process_image = plot_training_process(model_info, save_dir, request_id)
        model_info['train_process_image'] = train_process_image
        
        return model_info, model_save_path
        
    except Exception as e:
        log_progress(request_id, source_file_hash, "Error", f"训练失败: {str(e)}")
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
    model_select_info = {
        'task_type': 'clustering',
        'n_samples': n_samples,
        'n_features': df.shape[1]
    }
    
    if n_samples < 1000:
        model = KMeans(n_clusters=3)  # 小数据集使用K-means
    else:
        model = DBSCAN(eps=0.3, min_samples=10)  # 大数据集使用DBSCAN
    
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
        'n_classes': n_classes
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
        'n_features': n_features
    }
    
    return model, model_select_info

