from tinydb import TinyDB, Query
import time

# 初始化 TinyDB 数据库
db = TinyDB('./Test_TinyDB/training_progress.json')
progress_table = db.table('progress')


def get_training_status(request_id):
    """
    根据请求 ID 获取训练或测试的状态。

    参数:
    - request_id: 请求 ID,训练源文件的HASH

    返回:
    - 对应请求 ID 的训练状态和测试结果。
    """
    # 获取指定 request_id 的记录
    records = progress_table.search(Query().request_id == request_id)

    if records:
        print(f"Training/Testing Status for request ID: {request_id}\n")

        # 打印每个训练阶段的信息
        for record in records:
            print("-" * 40)  # 分隔线
            print(f"request_id: {record['request_id']}")
            print(f"Stage: {record['stage']}")
            print(f"Message: {record['message']}")
            print(f"Time: {record['time']}")

            # 打印训练时间（如果有的话）
            if 'training_time' in record:
                print(f"Training Time: {record['training_time']} seconds")

            # 打印模型评估结果（仅在评估阶段）
            if record['stage'] == 'Model Evaluation':
                if 'Accuracy' in record:
                    print(f"Accuracy: {record['Accuracy']:.4f}")
                if 'Precision' in record:
                    print(f"Precision: {record['Precision']:.4f}")
                if 'Recall' in record:
                    print(f"Recall: {record['Recall']:.4f}")
                if 'F1-Score' in record:
                    print(f"F1-Score: {record['F1-Score']:.4f}")
                if 'MSE' in record:
                    print(f"MSE: {record['MSE']:.4f}")
                if 'RMSE' in record:
                    print(f"RMSE: {record['RMSE']:.4f}")

            print("-" * 40)  # 分隔线
    else:
        print(f"No records found for request ID: {request_id}")


# 示例调用
if __name__ == '__main__':
    request_id = 'req_1'  # 假设这个请求 ID 是你想查询的
    get_training_status(request_id)
