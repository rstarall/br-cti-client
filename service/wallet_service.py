"""
    钱包服务
    用户账户生成
"""
from db.tiny_db import get_tiny_db_instance
from blockchain.user.wallet import genUserWallet
from blockchain.user.signature import ecc_sign_with_password
from blockchain.user.wallet import checkLocalUserAccountExist
from blockchain.user.signature import get_signature_nonce
from blockchain.user.wallet import getUserPublicKey
from blockchain.user.wallet import registerUserAccount
import base64
class WalletService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
    def checkUserAccountExist(self):
        """
            检查用户账户是否存在
            return:用户钱包ID or None
        """
        return checkLocalUserAccountExist()
    def getPublicKey(self, wallet_id: str):
        """
            获取用户公钥
            return:公钥,[]bytes
        """
        return getUserPublicKey(wallet_id)
    

    def eccSignature(self, wallet_id: str, password: str, message: str):
        """
            使用ecc签名
            return:签名结果,base64编码
        """
        return ecc_sign_with_password(wallet_id, password, message)
    def getSignatureNonce(self, wallet_id: str, password: str, message: str)->tuple[str,bool]:
        """
            获取签名随机数
            return:签名随机数,True or False
        """
        signature = self.eccSignature(wallet_id, password, message)
        return get_signature_nonce(wallet_id, password, signature)
    
    def createLocalUserWallet(self,password:str=None)->tuple[str,bool]:
        """
            生成本地用户账户
            password:用户密码，不能为空
            return:用户钱包ID,True or False
        """
        return genUserWallet(password)
    
    def registerUserAccount(self, wallet_id: str):
        """
            区块链上注册用户账户
            return:注册结果,True or False
        """
        public_pem = self.getPublicKey(wallet_id)
        public_pem = base64.b64decode(public_pem)
        return registerUserAccount(wallet_id, public_pem)

