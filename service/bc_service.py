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
from env.global_var import getUploadChainDataPath,getIpfsAddress
from blockchain.ipfs.ipfs import upload_file_to_ipfs,download_file_from_ipfs
from blockchain.fabric.cti_onchain import uploadCTIToBlockchain
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
    def getIPFSAddress(self):
        """
            获取IPFS地址
            return: IPFS地址
        """
        return getIpfsAddress()
    def uploadStixToIPFS(self,stix_file_path):
        """
            上传stix文件到IPFS
        """
        return upload_file_to_ipfs(stix_file_path)
    def downloadStixFromIPFS(self,ipfs_hash):
        """
            从IPFS下载stix文件
            return: 文件路径
        """
        return download_file_from_ipfs(ipfs_hash)
    
    
    def updateSTIXUpchainIPFSRecord(self,stix_file_hash,ipfs_hash):
        """
            更新STIX上传IPFS记录(IPFS)
        """
        try:
            if stix_file_hash=="" or ipfs_hash=="":
                return
            old_stix_upchain_records = self.tiny_db.use_database("stix_records").read_by_key_value("stix_records","stix_file_hash",stix_file_hash)
            if old_stix_upchain_records is not None and len(old_stix_upchain_records)>0:
                stix_file_path = old_stix_upchain_records[0].get("stix_file_path")
                if os.path.exists(stix_file_path):
                    read_stix_file_content = load_json_from_file(stix_file_path)
                    read_stix_file_content["ipfs_hash"] = ipfs_hash
                    read_stix_file_content["onchain"] = True
                    save_json_to_file(stix_file_path,read_stix_file_content)
            #更新记录
            old_stix_upchain_records[0]["ipfs_hash"] = ipfs_hash
            old_stix_upchain_records[0]["onchain"] = True
            self.tiny_db.use_database("stix_records").upsert_by_key_value("stix_records",old_stix_upchain_records[0],fieldName="stix_file_hash",value=stix_file_hash)
        except Exception as e:
            logging.error(f"updateSTIXUpchainRecord error:{e}")
    
    
    def updateSTIXUpchainRecord(self,stix_file_hash,cti_id=None,statistic_info_hash=None):
        """
            更新STIX上传区块链记录(链上ID)
        """
        try:
            old_stix_upchain_records = self.tiny_db.use_database("stix_records").read_by_key_value("stix_records","stix_file_hash",stix_file_hash)
            if old_stix_upchain_records is not None and len(old_stix_upchain_records)>0:
                stix_file_path = old_stix_upchain_records[0].get("stix_file_path")
                if os.path.exists(stix_file_path):
                    if cti_id is not None and statistic_info_hash is not None:
                        read_stix_file_content = load_json_from_file(stix_file_path)
                        read_stix_file_content["cti_id"] = cti_id
                        read_stix_file_content["statistic_info"] = statistic_info_hash
                        read_stix_file_content["onchain"] = True
                        save_json_to_file(stix_file_path,read_stix_file_content)
        except Exception as e:
            logging.error(f"updateSTIXUpchainRecord error:{e}")
    
    
    def updateCTIUpchainRecord(self,cti_hash,statistic_info_hash=None,cti_id=None):
        """
            更新CTI上传区块链记录(statistic_info_hash的IPFS_HASH,cti_id的链上ID)
        """
        old_cti_upchain_records = self.tiny_db.use_database("cti_records").read_by_key_value("cti_records","cti_hash",cti_hash)
        if old_cti_upchain_records is not None and len(old_cti_upchain_records)>0:
            cti_file_path = old_cti_upchain_records[0].get("cti_file_path")
            if os.path.exists(cti_file_path):
                read_cti_file_content = load_json_from_file(cti_file_path)
                if statistic_info_hash is not None:
                    read_cti_file_content["statistic_info"] = statistic_info_hash
                if cti_id is not None:
                    read_cti_file_content["cti_id"] = cti_id
                    read_cti_file_content["onchain"] = True
                save_json_to_file(cti_file_path,read_cti_file_content)
            if statistic_info_hash is not None:
                old_cti_upchain_records[0]["statistic_info"] = statistic_info_hash
            if cti_id is not None:
                old_cti_upchain_records[0]["cti_id"] = cti_id
                old_cti_upchain_records[0]["onchain"] = True
            self.tiny_db.use_database("cti_records").upsert_by_key_value("cti_records",old_cti_upchain_records[0],fieldName="cti_hash",value=cti_hash)
    
    
    def uploadCTIToBCByFileSourceHash(self, source_file_hash: str, upchain_account: str, upchain_account_password: str) -> tuple[str, bool]:
        """
            根据源文件hash值上传所有CTI数据到区块链
            source_file_hash: 源文件hash值
            upchain_account: 上链账号
            upchain_account_password: 上链账号密码
            return: (result,success)
        """
        # 获取本地CTI数据
        cti_data_list = self.data_service.get_local_cti_records_detail_list(source_file_hash)
        if len(cti_data_list) == 0:
            return "no_cti_data", False    
        # 初始化进度
        total_task_list = [i for i in range(len(cti_data_list))]
        self.updateCTIUpchainProgress(source_file_hash=source_file_hash,
                                    current_step=0,
                                    total_step=len(total_task_list),
                                    current_task_id=0,
                                    total_task_list=total_task_list)
                                    
        # 开启线程上传CTI数据到区块链
        thread = threading.Thread(
            target=self.startCTIUpchainTaskThread,
            args=(source_file_hash,cti_data_list, upchain_account, upchain_account_password)
        )
        thread.start()
        return f"start_cti_upchain_task_thread:{len(cti_data_list)}", True

    def startCTIUpchainTaskThread(self,source_file_hash:str, cti_data_list: list, wallet_id: str, wallet_password: str):
        """
            开启CTI上传区块链任务
            cti_data_list: CTI数据列表
            wallet_id: 钱包账号
            wallet_password: 钱包密码
        """
        for index, cti_data in enumerate(cti_data_list):
            #1.上传stix文件到IPFS
            try:    
                stix_file_path = cti_data.get("stix_data")
                if stix_file_path is not None and stix_file_path != "":
                    stix_file_hash,error = self.uploadStixFileToIPFS(stix_file_path)
                    if error is not None:
                        logging.error(f"uploadStixFileToIPFS error:{error}")
                        cti_data["stix_data"] = "upload stix file to ipfs error"
                        continue
                    #更新IPFS上传记录(cti_hash也是stix_file_hash)
                    self.updateSTIXUpchainIPFSRecord(cti_data.get("data_hash",""),stix_file_hash)
                    #更新CTI数据
                    cti_data["stix_data"] = stix_file_hash
                    cti_data["ipfs_hash"] = stix_file_hash
                else:
                    cti_data["stix_data"] = "stix file content is empty"
                    continue
            except Exception as e:
                logging.error(f"uploadStixFileToIPFS error:{e}")
                cti_data["stix_data"] = "upload stix file to ipfs error"
                continue

            #2.上传ioc_ips到IPFS
            statistic_file_ipfs_hash = None
            try:    
                statistic_info_path = self.data_service.get_cti_statistic_info_path(source_file_hash,cti_data.get("cti_hash"))
                if os.path.exists(statistic_info_path):
                    statistic_file_ipfs_hash,error = self.uploadStixFileToIPFS(statistic_info_path)
                    if error is not None:
                        logging.error(f"uploadStixFileToIPFS error:{error}")
                        cti_data["statistic_info"] = "upload statistic info to ipfs error"
                        continue
                    #更新CTI数据
                    cti_data["statistic_info"] = statistic_file_ipfs_hash
                    #更新CTI上传区块链记录
                    self.updateCTIUpchainRecord(cti_data.get("cti_hash"),
                                                statistic_info_hash=statistic_file_ipfs_hash,
                                                cti_id=None)
            except Exception as e:
                logging.error(f"getCTIStatisticInfoPath error:{e}")
                cti_data["statistic_info"] = "upload statistic info to ipfs error"
                continue

            #3.上传CTI数据到区块链
            cti_id = None
            try:
                cti_id = uploadCTIToBlockchain(wallet_id, wallet_password, cti_data)
                #更新CTI上传区块链记录
                self.updateCTIUpchainRecord(cti_data.get("cti_hash"),
                                                statistic_info_hash=None,
                                                cti_id=cti_id)
            except Exception as e:
                logging.error(f"uploadCTIToBlockchain error:{e}")
                continue
            #完全没有错误
            #1.更新STIX上链记录
            self.updateSTIXUpchainRecord(cti_data.get("cti_hash"),
                                         statistic_info_hash=statistic_file_ipfs_hash,
                                         cti_id=cti_id)
            #2.更新进度
            self.updateCTIUpchainProgress(source_file_hash,
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
                "source_file_hash":source_file_hash,
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
        #更新tinyDB
        self.tiny_db.use_database("cti_upchain_progress").upsert_by_key_value("cti_upchain_progress",
                                                                              self.cti_upchain_progress[source_file_hash],
                                                                              fieldName="source_file_hash",
                                                                              value=source_file_hash)
        
    def getCTIUpchainProgress(self,source_file_hash:str)->dict:
        """
            获取CTI上传区块链进度
            source_file_hash: 源文件hash值
            return: 进度信息
        """
        return self.cti_upchain_progress.get(source_file_hash,{})

    def uploadStixFileToIPFS(self,stix_file_path:str)->tuple[str,str]:
        """
            上传stix文件到IPFS
        """
        return upload_file_to_ipfs(stix_file_path)
    
    def downloadStixFileFromIPFS(self,ipfs_hash:str)->tuple[str,str]:
        """
            从IPFS下载stix文件
        """
        return download_file_from_ipfs(ipfs_hash)
