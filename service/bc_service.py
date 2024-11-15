"""
    blockchain service
    区块链服务
"""
from blockchain.fabric.fabric import checkBlockchainStatus
from db.tiny_db import TinyDBUtil
class BlockchainService:
    def __init__(self):
        self.tiny_db = TinyDBUtil()
    def checkBlockchainStatus():
        """
            检测区块链服务是否正常
            return: (blockInfo,is_ok)
        """
        return checkBlockchainStatus()