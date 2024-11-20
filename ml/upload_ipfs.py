import ipfshttpclient
import joblib
import os


def upload_model_to_ipfs(model_path):
    """
    上传模型文件至 IPFS，并返回文件的 hash 地址。

    参数:
    model_path (str): 模型文件路径

    返回:
    str: 上传后返回的 IPFS hash 地址
    """
    # 连接到本地或远程的 IPFS 节点
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')  # 本地IPFS节点

    # 检查文件是否存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    # 上传文件至 IPFS
    res = client.add(model_path)

    # 返回上传后文件的 hash
    return res['Hash']


# 示例：上传模型文件
if __name__ == '__main__':

    model_path = './save/DecisionTreeClassifier-req_8.joblib'  # 需要上传的模型文件路径
    ipfs_hash = upload_model_to_ipfs(model_path)
    print(f"Model uploaded to IPFS with hash: {ipfs_hash}")
