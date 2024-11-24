"""
    blockchain service
    区块链服务
"""
import threading
import os
from blockchain.fabric.block import checkBlockchainStatus,getBlockByHeight
from service.data_service import DataService
from db.tiny_db import get_tiny_db_instance
from utils.file import save_json_to_file,load_json_from_file
from env.global_var import getUploadChainDataPath
import logging
class BlockchainService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.cti_upchain_progress = {}
        self.upload_ipfs_data_progress = {}
        self.data_service = DataService()
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
    def uploadCTIToBCByFileSourceHash(self,source_file_hash:str)->tuple[str,bool]:
        """
            根据源文件hash值上传所有CTI数据到区块链
            source_file_hash: 源文件hash值
            return: (result,success)
        """
        # 获取本地CTI数据
        cti_data_list = self.data_service.get_local_cti_records_by_source_file_hash(source_file_hash)
        if len(cti_data_list) == 0:
            return "no_cti_data",False
        #初始化进度
        cti_data_list = [i for i in range(len(cti_data_list))]
        self.updateCTIUpchainProgress(source_file_hash=source_file_hash,
                                      current_step=0,
                                      total_step=len(cti_data_list),
                                      current_task_id=0,
                                      total_task_list=cti_data_list)
        #开启线程上传CTI数据到区块链
        thread = threading.Thread(target=self.startCTIUpchainTaskThread,args=(cti_data_list,))
        thread.start()
        return f"start_cti_upchain_task_thread:{len(cti_data_list)}",True
    def startCTIUpchainTaskThread(self,cti_data_list:list):
        """
            开启CTI上传区块链任务
        """
        for index,cti_data in enumerate(cti_data_list):
            try:
                self.uploadCTIToBlockchain(cti_data)
            except Exception as e:
                logging.error(f"uploadCTIToBlockchain error:{e}")
            #更新进度
            self.updateCTIUpchainProgress(cti_data["source_file_hash"],
                                          current_step=index+1,
                                          total_step=len(cti_data_list),
                                          current_task_id=index)

    def updateCTIUpchainProgress(self,source_file_hash:str,current_step=None,total_step=None,current_task_id=None,total_task_list=None):
        """
            更新CTI上传区块链进度
            
            param:
                - source_file_hash: 源文件的hash值
                - current_step: 当前步数
                - total_step: 总步数
                - current_task_id: 当前任务ID
                - total_task_list: 总任务列表
        """
        if total_task_list is not None:
            #初始化总任务列表
            total_task_list = list(total_task_list)
            self.cti_upchain_progress[source_file_hash] = {
                "progress":min(int((current_step/total_step)*100),100),
                "current_step":current_step,
                "total_step":total_step,
                "total_task_list":total_task_list,
                "current_task_id":current_task_id
            }
        else:
            #更新进度
            self.cti_upchain_progress[source_file_hash]["progress"] = min(int((current_step/total_step)*100),100)
            self.cti_upchain_progress[source_file_hash]["current_step"] = current_step
            self.cti_upchain_progress[source_file_hash]["total_step"] = total_step
            self.cti_upchain_progress[source_file_hash]["current_task_id"] = current_task_id
            #移出完成任务
            if current_task_id is not None:
                if current_task_id in self.cti_upchain_progress[source_file_hash]["total_task_list"]:
                    self.cti_upchain_progress[source_file_hash]["total_task_list"].remove(current_task_id)
    def getCTIUpchainProgress(self,source_file_hash:str)->dict:
        """
            获取CTI上传区块链进度
            source_file_hash: 源文件hash值
            return: 进度信息
        """
        return self.cti_upchain_progress.get(source_file_hash,{})
    def uploadCTIToBlockchain(self,cti_data:dict)->tuple[str,bool]:
        """
            上传CTI数据到区块链
        """
        pass
