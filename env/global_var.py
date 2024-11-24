import os

fabricServerHost = "http://localhost:7777"
userWalletPath = "blockchain/wallet"
uploadFilePath = "data/upload"
outputDirPath = "data/output"
mlUploadFilePath = "ml/upload"
mlOutputDirPath = "ml/output"
uploadChainDataPath = "blockchain/data/upload"
def _get_abs_path(relative_path, create_if_not_exists=False):
    """
    获取相对路径对应的绝对路径
    param:
        relative_path: 相对路径
        create_if_not_exists: 如果路径不存在是否创建
    return: str
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    abs_path = os.path.join(project_path, relative_path)
    if create_if_not_exists and not os.path.exists(abs_path):
        os.makedirs(abs_path)
    return abs_path

def getUserWalletAbsolutePath():
    """获取用户钱包绝对路径"""
    return _get_abs_path(userWalletPath, True)

def getOutputDirPath():
    """获取data client输出文件夹绝对路径"""
    return _get_abs_path(outputDirPath, True)

def getUploadFilePath():
    """获取data client上传文件夹绝对路径"""
    return _get_abs_path(uploadFilePath, True)

def getUploadChainDataPath():
    """获取上传链上数据文件夹绝对路径"""
    return _get_abs_path(uploadChainDataPath)



def updateFabricServerHost(host: str):
    """
        更新fabric-server地址
    """
    global fabricServerHost
    fabricServerHost = host

