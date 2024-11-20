
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
        return:公钥,[]bytes
    """
    with open(os.path.join(userWalletPath, wallet_id, 'public_key.pem'), 'rb') as f:
        public_pem = f.read()
    return public_pem

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

def registerUserAccount(wallet_id: str, public_pem):
    """
        使用公钥注册用户账户
        执行智能合约
        invoke fabric-server/registerUserAccount
        wallet_id:用户钱包ID
        public_pem:用户公钥,base64编码,解码后为[]bytes
    """
    try:
        response = request_post(fabricServerHost+"/registerUserAccount", data={"wallet_id": wallet_id, 
                                                                               "public_pem": public_pem})
        
        if "error" in response:
            return response["error"],False
        return response["data"],True
    except Exception as e:
        print(e)
        return str(e),False
