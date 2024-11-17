import os

fabricServerHost = "http://localhost:7777"
userWalletPath = "blockchain/wallet"

def getUserWalletAbsolutePath():
    """
        获取用户钱包绝对路径
    """
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    wallet_path = os.path.join(project_path, userWalletPath)
    
    if not os.path.exists(wallet_path):
        os.makedirs(wallet_path)
        
    return wallet_path

def updateFabricServerHost(host: str):
    """
        更新fabric-server地址
    """
    global fabricServerHost
    fabricServerHost = host

