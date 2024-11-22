import os

fabricServerHost = "http://localhost:7777"
userWalletPath = "blockchain/wallet"
uploadFilePath = "data/upload"
outputDirPath = "data/output"
mlUploadFilePath = "ml/upload"
mlOutputDirPath = "ml/output"
uploadChainDataPath = "blockchain/data/upload"
def getUserWalletAbsolutePath():
    """
        获取用户钱包绝对路径
        return: str
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    wallet_path = os.path.join(project_path, userWalletPath)
    
    if not os.path.exists(wallet_path):
        os.makedirs(wallet_path)
        
    return wallet_path

def getOutputDirPath():
    """
        获取data client输出文件夹绝对路径
        return: str
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    output_path = os.path.join(project_path, outputDirPath)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def getUploadFilePath():
    """
        获取data client上传文件夹绝对路径
        return: str
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    upload_path = os.path.join(project_path, uploadFilePath)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path
def getUploadChainDataPath():
    """
        获取上传链上数据文件夹绝对路径
        return: str
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    upload_chain_data_path = os.path.join(project_path, uploadChainDataPath)
    return upload_chain_data_path




def updateFabricServerHost(host: str):
    """
        更新fabric-server地址
    """
    global fabricServerHost
    fabricServerHost = host

