

import os
import logging
from utils.file import load_json_from_file
from env.global_var import getIPFSAddress

class IPFSService:
    def __init__(self):
        self.ipfs_address = None
        
    def getIPFSAddress(self) -> str:
        """
        获取IPFS地址
        """
        try:
            if self.ipfs_address is None:
                ipfs_config_path = os.path.join(os.path.dirname(__file__), "../config/ipfs_config.json")
                if os.path.exists(ipfs_config_path):
                    config = load_json_from_file(ipfs_config_path)
                    self.ipfs_address = config.get("ipfs_address", getIPFSAddress())
                else:
                    self.ipfs_address = getIPFSAddress()
            return self.ipfs_address
        except Exception as e:
            logging.error(f"getIPFSAddress error: {e}")
            return None
            
    def uploadFileToIPFS(self, file_path: str) -> tuple[str, str]:
        """
        上传文件到IPFS
        param:
            - file_path: 文件路径
        return:
            - ipfs_hash: IPFS哈希值
            - error: 错误信息
        """
        try:
            if not os.path.exists(file_path):
                return None, "文件不存在"
                
            # TODO: 实现IPFS上传逻辑
            ipfs_hash = "QmTest123"  # 临时返回测试hash
            return ipfs_hash, None
            
        except Exception as e:
            logging.error(f"uploadFileToIPFS error: {e}")
            return None, str(e)


