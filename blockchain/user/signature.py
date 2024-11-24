
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from env.global_var import getUserWalletAbsolutePath
from env.global_var import fabricServerHost
from utils.request import request_post
import base64


userWalletPath = getUserWalletAbsolutePath()

def ecc_sign(private_key:ec.EllipticCurvePrivateKey, tx_data: str)->tuple[str,bytes]:
    """
        对消息进行签名
        :param private_key:私钥
        :param message:消息
        :return 签名结果,消息字节(utf-8编码)
    """
    message_bytes = tx_data.encode() #utf-8编码
    # 计算消息的哈希值(SHA256)
    message_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    message_hash.update(message_bytes) 
    digest = message_hash.finalize()
    # 签名,ec.ECDSA(hashes.SHA256())指定签名算法
    # 签名输出为ASN.1 DER格式
    signature = private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
    # 将签名结果编码为Base64
    return base64.b64encode(signature).decode(),message_bytes



def ecc_sign_with_password(wallet_id: str, password: str, tx_data: str)->str:
    with open(os.path.join(userWalletPath, wallet_id, 'private_key.pem'), 'rb') as f:
        pem_data = f.read()
    #加载并解密私钥
    private_key = load_encrypted_private_key(pem_data, password)
    return ecc_sign(private_key, tx_data)

def load_encrypted_private_key(pem_data: bytes, password: str)->ec.EllipticCurvePrivateKey:
    """
        从加密的PEM数据加载私钥
        return:私钥
    """
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=password.encode(),
        backend=default_backend()
    )
    return private_key

def load_public_key(pem_data: bytes)->ec.EllipticCurvePublicKey:
    """
        从PEM数据加载公钥
        return:公钥
    """
    return serialization.load_pem_public_key(pem_data, backend=default_backend())

