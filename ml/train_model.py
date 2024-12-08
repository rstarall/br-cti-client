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



def feature_engineering(df,model_info={}, target_column=None):
    """
        对清洗后的数据集进行特征工程。
        参数：
        df -- 输入的DataFrame数据
        model_info -- 模型信息(记录每个阶段的处理方式)
        target_column -- 目标列的列名，如果有目标列的话，应该排除该列进行处理
    """

    # 1. 特征缩放：对数值特征进行标准化
    numerical_columns = df.select_dtypes(include=[np.number]).columns
    if target_column:
        numerical_columns = numerical_columns[numerical_columns != target_column]

    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    # 2. 类别特征编码：对对象类型列进行独热编码
    categorical_columns = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=categorical_columns)

    # 3. 特征交互：生成多项式特征
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    poly_features = poly.fit_transform(df[numerical_columns])
    poly_columns = poly.get_feature_names_out(numerical_columns)
    df_poly = pd.DataFrame(poly_features, columns=poly_columns)

    # 拼接生成的多项式特征
    df = pd.concat([df, df_poly], axis=1)

    # 4. 降维：使用PCA降低特征维度
    pca = PCA(n_components=10)  # 保留10个主成分
    pca_features = pca.fit_transform(df)
    #保存主成分信息
    model_info['pca'] = pca.explained_variance_ratio_.tolist()
    print(model_info)
    return df, model_info

def train_and_save_model(request_id,source_file_hash,output_dir_path, df, target_column, callback=None):
    """
        训练并保存模型，同时记录训练过程中的每个阶段的进度。
        参数：

        df -- 输入的DataFrame数据
        source_file_hash -- 数据源文件的hash值
        output_dir_path -- 文件保存路径
        target_column -- 目标列的列名(label)
        callback -- 回调函数
        返回：
        model_info -- 模型信息
        model_save_path -- 模型保存路径
    """
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
    # 记录训练开始时间
    start_time = time.time()
    # 1. 特征工程
    print('开始特征工程...')
    log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering started", training_time=0)
    df, model_info = feature_engineering(df, model_info, target_column)  # 特征工程步骤
    print('特征工程完成！')
    log_progress(request_id, source_file_hash, "Feature Engineering", "Feature engineering completed", training_time=time.time() - start_time)

    # 编码类别型特征
    print("开始类别型特征编码...")
    log_progress(request_id, source_file_hash, "Label Encoding", "Label encoding started", training_time=0)
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    log_progress(request_id, source_file_hash, "Label Encoding", "Label encoding completed", training_time=time.time() - start_time)  # 记录进度

    # 2. 划分特征和标签
    X = df.drop(columns=[target_column])
    y = df[target_column]
    model_info["target_column"] = target_column
    # 3. 划分训练集和测试集
    print("开始划分训练集和测试集...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    log_progress(request_id, source_file_hash,"Train/Test Split", "Train/test split completed", training_time=time.time() - start_time)  # 记录进度
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
    log_progress(request_id,source_file_hash, "Model Training", "Training started", training_time=time.time() - start_time)

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
    log_progress(request_id,source_file_hash, "Model Training", "Training completed", training_time=time.time() - start_time)
    # 6. 保存模型
    save_dir = output_dir_path+'/save'
    os.makedirs(save_dir, exist_ok=True)
    model_save_path = os.path.join(save_dir, f"{request_id}-{model_name}.joblib")
    joblib.dump(model, model_save_path)
    model_info["model_save_path"] = model_save_path
    log_progress(request_id,source_file_hash, "Model Saving", f"Model save success", training_time=time.time() - start_time)

    # 在模型训练完成后更新模型信息
    model_info.update({
        "model_algorithm": model.__class__.__name__,  # 记录具体使用的算法
        "model_type": 1 if model_select_info.get('task_type') == 'classification' else 2,  # 根据任务类型设置模型类型
        "model_size": os.path.getsize(model_save_path)  # 记录模型文件大小
    })

    return model_info, model_save_path



def select_model_based_on_features(df, target_column):
    """
        根据特征选择合适的模型。
        参数：
        request_id -- 请求ID
        source_file_hash -- 数据源文件hash
        df -- 输入的DataFrame数据
        target_column -- 目标列的列名(label)
        返回：
        model -- 模型
        model_select_info -- 模型选择信息
    """
    # 获取目标列的数据类型
    target_dtype = df[target_column].dtype

    # 确定任务类型：回归或分类
    # 如果目标列是数值类型，并且是浮动型数据，则为回归任务
    if target_dtype in [np.float64, np.int64]:
        # 检查目标列的唯一值数量，如果值的数量小于等于一定数量则认为是分类任务
        n_unique_values = df[target_column].nunique()
        if n_unique_values <= 10:  # 设置一个阈值，少于等于10个唯一值的数值型目标列视为分类任务
            task_type = 'classification'
        else:
            task_type = 'regression'
    else:
        # 如果目标列是对象类型，认为是分类任务
        task_type = 'classification'

    # 获取样本量和特征数量
    n_samples, n_features = df.shape

    # 获取特征类型：数值型和类别型特征数量
    numeric_features = df.select_dtypes(include=[np.number]).columns
    categorical_features = df.select_dtypes(exclude=[np.number]).columns

    # 简单的模型选择逻辑
    if task_type == 'classification':
        n_classes = df[target_column].nunique()
        
        if n_samples < 1000:
            # 小数据集优先选择逻辑回归，它简单且不容易过拟合
            model = LogisticRegression(
                max_iter=1000,
                warm_start=True,
                solver='lbfgs'
            )
        elif len(categorical_features) > len(numeric_features):
            # 特征中类别变量较多，使用随机森林
            model = RandomForestClassifier(
                n_estimators=100,
                warm_start=True,
                n_jobs=-1,
                max_depth=None,  # 允许树充分生长
                min_samples_split=2,
                min_samples_leaf=1
            )
        else:
            # 数值特征为主，可以考虑SVM
            # 如果样本量较大，使用更快的'rbf'核
            if n_samples > 10000:
                model = SVC(
                    kernel='rbf',
                    probability=True,
                    cache_size=2000  # 增加缓存大小以提高性能
                )
            else:
                model = SVC(
                    kernel='rbf',
                    probability=True
                )
    else:  # 回归任务
        if n_samples < 1000:
            model = LinearRegression()  # 小数据量用简单的线性回归
        elif n_features > 10:
            model = RandomForestRegressor(
                n_estimators=100,
                warm_start=True,
                n_jobs=-1,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1
            )
        else:
            model = SVR(kernel='rbf')  # 数据量适中且特征较少时使用SVR

    # 添加模型支持的训练方式信息
    model.supports_iterative_training = isinstance(model, (
        RandomForestClassifier, 
        RandomForestRegressor,
        LogisticRegression  # 逻辑回归也支持迭代训练
    ))
    
    print(f"选择的模型: {model.__class__.__name__}")
    print(f"支持迭代训练: {model.supports_iterative_training}")
    
    # 打印模型选择的依据
    print("\n模型选择依据:")
    print(f"- 数据量: {n_samples} 条")
    print(f"- 特征数: {n_features} 个")
    print(f"- 数值特征: {len(numeric_features)} 个")
    print(f"- 类别特征: {len(categorical_features)} 个")
    if task_type == 'classification':
        print(f"- 类别数量: {n_classes} 个")
    model_select_info = {
        'task_type': task_type,
        'n_samples': n_samples,
        'n_features': n_features,
        'numeric_features': len(numeric_features),
        'categorical_features': len(categorical_features),
        'n_classes': n_classes
    }
    return model,model_select_info

