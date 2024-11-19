"""
    blockchain service
    区块链服务
"""
from blockchain.fabric.fabric import checkBlockchainStatus,getBlockByHeight
from db.tiny_db import get_tiny_db_instance
class BlockchainService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
    def checkBlockchainStatus(self):
        """
            检测区块链服务是否正常
            return: (blockInfo,is_ok)
        """
        return checkBlockchainStatus()
    def getBlockByHeight(self, height):
        """
            根据高度获取区块信息
            height: 区块高度
            return: (blockInfo,is_ok)
        """
        return getBlockByHeight(height)