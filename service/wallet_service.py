"""
    钱包服务
    用户账户生成
"""
from db.tiny_db import get_tiny_db_instance
from blockchain.user.wallet import genUserWallet
from blockchain.user.signature import ecc_sign_with_password
from blockchain.user.wallet import checkLocalUserAccountExist
from blockchain.fabric.tx import getTransactionNonce
from blockchain.user.wallet import getUserPublicKey,checkWalletPassword
from blockchain.fabric.user_onchain import registerUserOnchain
from blockchain.user.wallet import checkLocalWalletOnchainStatus,getLocalUserAccountMulti
from blockchain.fabric.cti_onchain import purchaseCTIFromBlockchain,createCTIPurchaseTransaction
from blockchain.fabric.ml_onchain import purchaseModelFromBlockchain,createModelPurchaseTransaction
from blockchain.fabric.user_onchain import getUserCTIStatistics
import base64
class WalletService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
    def checkUserAccountExist(self,wallet_id:str=None):
        """
            检查用户账户是否存在
            return:用户钱包ID or None
        """
        return checkLocalUserAccountExist(wallet_id)
    def getLocalUserAccountMulti(self):
        """
            获取用户钱包列表(多个钱包)
            return:钱包ID列表
        """
        return getLocalUserAccountMulti()
    def checkLocalWalletOnchainStatus(self,wallet_id:str)->str:
        """
            检查本地钱包是否已上链
            return:上链钱包ID or None
        """
        return checkLocalWalletOnchainStatus(wallet_id)
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
    
    def getSignatureNonce(self, wallet_id: str, password: str, tx_sign: str)->tuple[str,bool]:
        """
            获取签名随机数
            return:签名随机数,True or False
        """
        return getTransactionNonce(wallet_id, password, tx_sign)
    
    def createLocalUserWallet(self,password:str=None)->tuple[str,bool]:
        """
            生成本地用户账户

            param:
                - password:用户密码，不能为空

            return:
                - str:用户钱包ID
                - bool:True or False
        """
        return genUserWallet(password)
    
    def registerOnchainUserAccount(self, wallet_id: str, user_name: str)->tuple[str,bool]:
        """
            区块链上注册用户账户

            param:
                - wallet_id:用户钱包ID
                - user_name:用户名称(可选)
            return:
                - bool:True or False
        """
        #检查本地账户一致性
        wallet_ids = getLocalUserAccountMulti()
        if wallet_id not in wallet_ids:
            return "local user account not exist",False
        return registerUserOnchain(wallet_id, user_name)

    def checkWalletPassword(self, wallet_id: str, password: str)->bool:
        """
            检查钱包密码
            param:
                - wallet_id: 钱包ID
                - password: 钱包密码
            return:
                - bool: 密码是否正确
        """
        return checkWalletPassword(wallet_id, password)
    
    def createCTIPurchaseTransaction(self, wallet_id:str, password:str, cti_id:str)->dict:
        """
            创建CTI购买交易(签名结构)
        """
        return createCTIPurchaseTransaction(wallet_id, password, cti_id)
    
    def purchaseCTIFromBlockchain(self, wallet_id:str, password:str, cti_id:str)->tuple[str,bool]:
        """
            从区块链购买CTI
        """
        return purchaseCTIFromBlockchain(wallet_id, password, cti_id)
    
    def createModelPurchaseTransaction(self, wallet_id:str, password:str, model_id:str)->dict:
        """
            创建模型购买交易(签名结构)
        """
        return createModelPurchaseTransaction(wallet_id, password, model_id)
    
    def purchaseModelFromBlockchain(self, wallet_id:str, password:str, model_id:str)->tuple[str,bool]:
        """
            从区块链购买模型
        """
        return purchaseModelFromBlockchain(wallet_id, password, model_id)

    def getUserCTIStatistics(self, user_id: str)->tuple[dict,bool]:
        """
            获取用户CTI统计数据
            param:
                - user_id: 用户ID
            return:
                - dict: 用户CTI统计数据
                - bool: 是否成功
        """
        return getUserCTIStatistics(user_id)