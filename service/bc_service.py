"""
    blockchain service
    区块链服务
"""
from blockchain.fabric.fabric import checkBlockchainStatus,getBlockByHeight
from db.tiny_db import get_tiny_db_instance
class BlockchainService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.upload_cti_data_progress = {}
        self.upload_ipfs_data_progress = {}
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
    def uploadStixToIPFS(self,stix_file_path):
        """
            上传stix文件到IPFS
        """
        pass
    def uploadCTIToBlockchain(self,cti_data):
        """
            上传CTI数据到区块链
        """
        pass
