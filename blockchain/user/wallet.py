
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes as crypto_hashes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from blockchain.user.signature import load_public_key
from env.global_var import getUserWalletAbsolutePath
from utils.request import request_post
from env.global_var import fabricServerHost
import json
import base64
import os

userWalletPath = getUserWalletAbsolutePath()

def checkLocalUserAccountExist():
    """
        查询用户钱包是否存在
        retrun:第一个钱包ID or None
    """
    userWalletPath = getUserWalletAbsolutePath()
    #检测wallet文件夹下所有钱包文件夹是否存在
    for wallet_id in os.listdir(userWalletPath):
        if  os.path.exists(os.path.join(userWalletPath, wallet_id, 'public_key.pem')):
            if os.path.exists(os.path.join(userWalletPath, wallet_id, 'private_key.pem')):
                return wallet_id
    return None

def checkLocalWalletOnchainStatus(wallet_id:str)->str:
    """
        检查本地钱包是否已上链
        return:上链钱包ID or None
    """
    userWalletPath = getUserWalletAbsolutePath()
    #检测wallet文件夹下所有钱包文件夹是否存在
    wallet_dir = os.path.join(userWalletPath, wallet_id)
    if not os.path.exists(wallet_dir):
        return None
    #遍历文件夹下所有以_onchain.json结尾的文件
    for file_name in os.listdir(wallet_dir):
        if file_name.endswith("wallet_status.json"):
            onchain_file_path = os.path.join(wallet_dir, file_name)
            with open(onchain_file_path, 'r') as f:
                onchain_data = json.load(f)
                if onchain_data.get("onchain"):
                    if onchain_data.get("onchain_wallet_id",None) is not None:
                        return onchain_data.get("onchain_wallet_id")
    return None

def getLocalUserWalletId():
    """
        获取本地用户钱包ID
        return:用户钱包ID
    """
    return checkLocalUserAccountExist()

def getUserWalletId(public_pem: bytes):
    """
        对公钥进行sha256以获取用户钱包ID
        public_pem:公钥PEM格式,[]bytes
        return:用户钱包ID
    """
    message_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    message_hash.update(public_pem)
    digest = message_hash.finalize()
    return digest.hex()

def getUserPublicKey(wallet_id: str):
    """
        获取用户公钥
        return:公钥,str
    """
    with open(os.path.join(userWalletPath, wallet_id, 'public_key.pem'), 'rb') as f:
        public_pem = f.read()

    return str(public_pem)

def genUserWallet(password=None)->tuple[str,bool]:
    """
        生成用户公私钥或证书，保存在wallet文件夹下
        password:用户密码，如果为空，使用空字符串加密
        return:用户钱包ID
    """
    userWalletPath = getUserWalletAbsolutePath()
    if password is None:
        password = ""
    try:
        private_key, encrypted_private_pem, public_pem = genEccPubAndPriKey(password)
        wallet_id = getUserWalletId(public_pem)
        userWalletPath = os.path.join(userWalletPath, wallet_id) 
        #如果用户钱包文件夹不存在，则创建
        if not os.path.exists(userWalletPath):
            os.makedirs(userWalletPath)
        #保存私钥
        with open(os.path.join(userWalletPath, 'private_key.pem'), 'wb') as f:
            f.write(encrypted_private_pem)
        #保存公钥
        with open(os.path.join(userWalletPath, 'public_key.pem'), 'wb') as f:
            f.write(public_pem)
        return wallet_id,True
    except Exception as e:
        return str(e),False
    

def genEccPubAndPriKey(password: str)->tuple[ec.EllipticCurvePrivateKey, bytes, bytes]:
    """
        生成椭圆曲线公私钥
        password:用户密码，如果为空，使用空字符串加密
        return:私钥，加密私钥，公钥
    """
    # 生成椭圆曲线密钥对
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    # 使用密码加密私钥
    encrypted_private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, encrypted_private_pem, public_pem

def checkWalletPassword(wallet_id: str, password: str)->bool:
    """
        检查钱包密码
        param:
            - wallet_id: 钱包ID
            - password: 钱包密码
        return:
            - bool: 密码是否正确
    """
    try:
        # 获取钱包路径
        userWalletPath = getUserWalletAbsolutePath()
        walletPath = os.path.join(userWalletPath, wallet_id)
        
        # 读取私钥文件
        with open(os.path.join(walletPath, 'private_key.pem'), 'rb') as f:
            encrypted_private_pem = f.read()
            
        # 尝试使用密码解密私钥
        serialization.load_pem_private_key(
            encrypted_private_pem,
            password=password.encode(),
            backend=default_backend()
        )
        return True
    except Exception as e:
        return False
    
