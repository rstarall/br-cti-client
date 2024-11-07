"""
    钱包服务
    用户账户生成
"""
from db.tiny_db import TinyDBUtil
from blockchain.user.wallet import genUserAccount
class WalletService:
    def __init__(self):
        self.tiny_db = TinyDBUtil()
    def genUserAccount():
        """
            生成用户账户
        """
        genUserAccount()
    def rsaSignature():
        pass