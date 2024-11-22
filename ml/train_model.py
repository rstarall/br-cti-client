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

# 初始化 TinyDB 数据库
db = TinyDB('./Test_TinyDB/training_progress.json')
progress_table = db.table('progress')

# 自动生成请求 ID
def generate_request_id():
    return 'req_1'  # 返回固定的请求ID，如果需要动态生成可以使用 UUID
    # return str(uuid.uuid4())

def feature_engineering(df, target_column=None):
    """
    对清洗后的数据集进行特征工程。
    参数：
    df -- 输入的DataFrame数据
    target_column -- 目标列的列名，如果有目标列的话，应该排除该列进行处理
    """
    request_id = generate_request_id()  # 自动生成请求ID

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

    return df

def train_and_save_model(df, target_column):
    """
    训练并保存模型，同时记录训练过程中的每个阶段的进度。
    参数：
    df -- 输入的DataFrame数据
    target_column -- 目标列的列名
    """
    request_id = generate_request_id()  # 自动生成请求ID

    # 记录训练开始时间
    start_time = time.time()

    # 1. 特征工程
    print('开始特征工程...')
    log_progress(request_id, "Feature Engineering", "Feature engineering started", training_time=0)
    df = feature_engineering(df, target_column)  # 特征工程步骤
    print('特征工程完成！')
    log_progress(request_id, "Feature Engineering", "Feature engineering completed", training_time=time.time() - start_time)

    # 编码类别型特征
    print("开始类别型特征编码...")
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    log_progress(request_id, "Label Encoding", "Label encoding completed", training_time=time.time() - start_time)  # 记录进度

    # 2. 划分特征和标签
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # 3. 划分训练集和测试集
    print("开始划分训练集和测试集...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    log_progress(request_id, "Train/Test Split", "Train/test split completed", training_time=time.time() - start_time)  # 记录进度

    # 4. 根据特征选择合适的模型
    model = select_model_based_on_features(df, target_column)
    model_name = model.__class__.__name__

    # 记录开始训练的时间
    log_progress(request_id, "Model Training", "Training started", training_time=time.time() - start_time)

    # 5. 训练模型
    model_start_time = time.time()
    model.fit(X_train, y_train)
    model_training_time = time.time() - model_start_time
    log_progress(request_id, "Model Training", f"Training completed in {model_training_time:.2f} seconds", training_time=model_training_time)

    # 6. 保存模型
    save_dir = './save'
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, f"{model_name}-{request_id}.joblib")
    joblib.dump(model, model_path)

    log_progress(request_id, "Model Saving", f"Model saved to {model_path}", training_time=time.time() - start_time)

    return request_id

def log_progress(request_id, stage, message, training_time=None):
    """
    记录训练进度和时间，保存请求ID和训练时间。
    参数：
    request_id -- 请求 ID，用于标识训练任务
    stage -- 当前阶段（例如：训练开始、训练完成、评估等）
    message -- 阶段描述消息
    training_time -- 训练时间，单位为秒（可选）
    """
    # 将进度记录到 TinyDB 中
    progress_table.upsert({
        'request_id': request_id,
        'stage': stage,
        'message': message,
        'training_time': training_time,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }, Query().request_id == request_id)

    # 输出当前阶段的进度
    print(f"{stage}: {message} (Elapsed Time: {training_time:.2f}s)" if training_time else f"{stage}: {message}")

def select_model_based_on_features(df, target_column):
    """
    根据特征选择合适的模型。
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
        if n_samples < 1000:
            model = DecisionTreeClassifier()  # 小数据量分类
        elif len(categorical_features) > len(numeric_features):
            model = RandomForestClassifier()  # 多类别特征适合随机森林
        else:
            model = SVC()  # 数值特征适合 SVM
    else:  # 回归任务
        if n_samples < 1000:
            model = DecisionTreeRegressor()  # 小数据量回归
        elif n_features > 10:
            model = RandomForestRegressor()  # 多特征时使用随机森林回归
        else:
            model = LinearRegression()  # 简单线性回归

    print(f"选择的模型: {model.__class__.__name__}")
    return model

# 示例调用
# 假设数据集已加载为 df，目标列名为 'target'
if __name__ == '__main__':
    df = pd.read_csv('./dataset/cleaned_dataset.csv')
    train_and_save_model(df, 'label')
