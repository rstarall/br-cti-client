"""
    blockchain service
    区块链服务
"""
import threading
import os
from blockchain.fabric.block import checkBlockchainStatus,getBlockByHeight
from service.data_service import DataService
from service.ml_service import MLService
from db.tiny_db import get_tiny_db_instance
from utils.file import save_json_to_file,load_json_from_file
from env.global_var import getUploadChainDataPath,getIpfsAddress
from blockchain.ipfs.ipfs import upload_file_to_ipfs,download_file_from_ipfs
from blockchain.fabric.cti_onchain import uploadCTIToBlockchain,createCTIUploadTransaction
from blockchain.fabric.ml_onchain import uploadModelToBlockchain,createModelUploadTransaction
import logging
class BlockchainService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.cti_upchain_progress = {}
        self.upload_ipfs_data_progress = {}
        self.data_service = DataService()
        self.ml_service = MLService()
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
    def createCTIUploadTransaction(self,wallet_id:str, password:str, cti_data:dict)->dict:
        """
            创建CTI上传链签名交易
        """
        return createCTIUploadTransaction(wallet_id, password, cti_data)
    
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
            # 1. 上传数据源文件到IPFS
            data_source_ipfs_hash = None
            try:
                data_source_path = self.data_service.get_upload_file_path_by_hash(source_file_hash)
                if data_source_path and data_source_path != "":
                    data_source_ipfs_hash, error = self.uploadFileToIPFS(data_source_path)
                    if error:
                        logging.error(f"uploadStixFileToIPFS error:{error}")
                        continue
                    # 更新数据源IPFS地址
                    cti_data["data_source_hash"] = source_file_hash
                    cti_data["data_source_ipfs_hash"] = data_source_ipfs_hash
                else:
                    logging.error("data source file is empty")
                    continue
            except Exception as e:
                logging.error(f"uploadStixFileToIPFS error:{e}")
                continue

            # 2. 上传stix文件到IPFS
            try:
                stix_file_path = cti_data.get("stix_data") 
                if stix_file_path and stix_file_path != "":
                    stix_ipfs_hash, error = self.uploadStixFileToIPFS(stix_file_path)
                    if error:
                        logging.error(f"uploadStixFileToIPFS error:{error}")
                        continue
                    # 更新STIX IPFS地址
                    cti_data["stix_ipfs_hash"] = stix_ipfs_hash
                    # 更新IPFS上传记录
                    self.updateSTIXUpchainIPFSRecord(cti_data.get("cti_hash",""), stix_ipfs_hash)
                else:
                    logging.error("stix file content is empty")
                    continue
            except Exception as e:
                logging.error(f"uploadStixFileToIPFS error:{e}") 
                continue

            # 3. 上传统计信息到IPFS
            try:
                statistic_info_path = self.data_service.get_cti_statistic_info_path(source_file_hash, cti_data.get("cti_hash"))
                if os.path.exists(statistic_info_path):
                    statistic_ipfs_hash, error = self.uploadFileToIPFS(statistic_info_path)
                    if error:
                        logging.error(f"uploadStixFileToIPFS error:{error}")
                        continue
                    # 更新统计信息IPFS地址
                    cti_data["statistic_info"] = statistic_ipfs_hash
                    # 更新CTI上传记录
                    self.updateCTIUpchainRecord(cti_data.get("cti_hash"), 
                                              statistic_info_hash=statistic_ipfs_hash,
                                              cti_id=None)
            except Exception as e:
                logging.error(f"upload statistic info error:{e}")
                continue

            # 4. 上传CTI数据到区块链
            try:
                result, success = uploadCTIToBlockchain(wallet_id, wallet_password, cti_data)
                if success and result:
                    cti_id = result.get("cti_id")
                    # 更新CTI上传记录
                    self.updateCTIUpchainRecord(cti_data.get("cti_hash"),
                                              statistic_info_hash=None, 
                                              cti_id=cti_id)
                    # 更新STIX上链记录
                    self.updateSTIXUpchainRecord(cti_data.get("cti_hash"),
                                               statistic_info_hash=statistic_ipfs_hash,
                                               cti_id=cti_id)
                else:
                    raise Exception(result)
            except Exception as e:
                logging.error(f"uploadCTIToBlockchain error:{e}")
                continue

            # 更新进度
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
    
    #-----------------------------------------------------模型上链--------------------------------------------------------------------
    def uploadModelToBCByFileSourceHash(self, source_file_hash: str, upchain_account: str, upchain_account_password: str) -> tuple[str, bool]:
        """
            根据源文件hash值上传所有模型数据到区块链
            source_file_hash: 源文件hash值
            upchain_account: 上链账号
            upchain_account_password: 上链账号密码
            return: (result,success)
        """
        # 获取本地模型数据
        model_record_detail_list = self.ml_service.getModelRecordsDetailList(source_file_hash)
        if len(model_record_detail_list) == 0:
            return "no_model_data", False
            
        # 初始化进度
        total_task_list = [i for i in range(len(model_record_detail_list))]
        self.updateModelUpchainProgress(source_file_hash=source_file_hash,
                                    current_step=0,
                                    total_step=len(total_task_list),
                                    current_task_id=0,
                                    total_task_list=total_task_list)
                                    
        # 开启线程上传模型数据到区块链
        thread = threading.Thread(
            target=self.startModelUpchainTaskThread,
            args=(source_file_hash, model_record_detail_list, upchain_account, upchain_account_password)
        )

        thread.start()
        return f"start_model_upchain_task_thread:{len(model_record_detail_list)}", True
    
    def uploadModelToBCByModelHash(self, source_file_hash: str, model_hash: str, upchain_account: str, upchain_account_password: str) -> tuple[str, bool]:
        """
            根据模型hash值上传模型数据到区块链
            source_file_hash: 源文件hash值
            model_hash: 模型hash值
            upchain_account: 上链账号
            upchain_account_password: 上链账号密码
            return: (result,success)
        """
        # 获取模型记录详情
        model_record_detail = self.ml_service.getModelRecordByHashAndHash(source_file_hash,model_hash)
        if model_record_detail is None:
            return "no_model_data", False
            
        # 初始化进度
        total_task_list = [0]
        self.updateModelUpchainProgress(source_file_hash=source_file_hash,
                                    current_step=0,
                                    total_step=1,
                                    current_task_id=0,
                                    total_task_list=total_task_list)
                                    
        # 开启线程上传模型数据到区块链
        thread = threading.Thread(
            target=self.startModelUpchainTaskThread,
            args=(source_file_hash, [model_record_detail], upchain_account, upchain_account_password)
        )

        thread.start()
        return "start_model_upchain_task_thread:1", True
    
    def startModelUpchainTaskThread(self, source_file_hash:str, model_record_detail_list: list, wallet_id: str, wallet_password: str):
        """
            开启模型上传区块链任务
            model_record_detail_list: 模型记录详情列表
            wallet_id: 钱包账号
            wallet_password: 钱包密码
        """
        for index, model_record_detail in enumerate(model_record_detail_list):
            try:
                model_hash = model_record_detail.get("model_hash","")
                model_path = self.ml_service.getModelUpchainInfoFilePath(source_file_hash, model_hash)
                
                # 1. 上传模型文件到IPFS
                if model_path and os.path.exists(model_path):
                    model_ipfs_hash, error = self.uploadModelFileToIPFS(model_path)
                    if error:
                        logging.error(f"uploadModelFileToIPFS error:{error}")
                        continue
                    # 更新模型IPFS地址
                    self.ml_service.saveModelUpchainResult(source_file_hash, model_hash, model_ipfs_hash, "")
                else:
                    logging.error("model file not found")
                    continue    

                # 2. 上传模型数据到区块链
                try:
                    result, success = uploadModelToBlockchain(wallet_id, wallet_password, model_record_detail)
                    if success and result:
                        model_id = result.get("model_id")
                        # 更新模型上传记录
                        self.updateModelUpchainRecord(model_hash, model_id)
                    else:
                        raise Exception(result)
                except Exception as e:
                    logging.error(f"uploadModelToBlockchain error:{e}")
                    continue

            except Exception as e:
                logging.error(f"startModelUpchainTaskThread error:{e}")
                continue

            # 更新进度
            self.updateModelUpchainProgress(source_file_hash,
                                        current_step=index+1,
                                        total_step=len(model_record_detail_list),
                                        current_task_id=index)
            
    def updateModelUpchainRecord(self, model_hash:str, model_id:str):
        """
            更新模型上传区块链记录(链上ID)
        """
        try:
            old_model_records = self.tiny_db.use_database("ml_records").read_by_key_value("ml_records","model_hash",model_hash)
            if old_model_records is not None and len(old_model_records)>0:
                new_model_record = old_model_records[0]
                new_model_record["model_id"] = model_id
                new_model_record["onchain"] = True
                self.tiny_db.use_database("ml_records").upsert_by_key_value("ml_records",
                                                                            new_model_record,
                                                                          fieldName="model_hash",
                                                                          value=model_hash)
        except Exception as e:
            logging.error(f"updateModelUpchainRecord error:{e}")
        
    def updateModelUpchainProgress(self, source_file_hash:str, current_step=None, total_step=None, current_task_id=None, total_task_list=None):
        """
            更新模型上传区块链进度
            
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
            self.model_upchain_progress[source_file_hash] = {
                "source_file_hash":source_file_hash,
                "progress":min(int((current_step/total_step)*100),100),
                "current_step":current_step,
                "total_step":total_step,
                "total_task_list":total_task_list,
                "current_task_id":current_task_id
            }
        else:
            #更新进度
            self.model_upchain_progress[source_file_hash]["progress"] = min(int((current_step/total_step)*100),100)
            self.model_upchain_progress[source_file_hash]["current_step"] = current_step
            self.model_upchain_progress[source_file_hash]["total_step"] = total_step
            self.model_upchain_progress[source_file_hash]["current_task_id"] = current_task_id
            #移出完成任务
            if current_task_id is not None:
                if current_task_id in self.model_upchain_progress[source_file_hash]["total_task_list"]:
                    self.model_upchain_progress[source_file_hash]["total_task_list"].remove(current_task_id)
        #更新tinyDB
        self.tiny_db.use_database("model_upchain_progress").upsert_by_key_value("model_upchain_progress",
                                                                              self.model_upchain_progress[source_file_hash],
                                                                              fieldName="source_file_hash",
                                                                              value=source_file_hash)

    def getModelUpchainProgress(self, source_file_hash:str)->dict:
        """
            获取模型上传区块链进度
            source_file_hash: 源文件hash值
            return: 进度信息
        """
        return self.model_upchain_progress.get(source_file_hash,{})



    def uploadFileToIPFS(self,file_path:str)->tuple[str,str]:
        """
            上传数据到IPFS
            file_path: 文件路径
            return: (ipfs_hash,error)
        """
        return upload_file_to_ipfs(file_path)
    def uploadStixFileToIPFS(self,stix_file_path:str)->tuple[str,str]:
        """
            上传stix文件到IPFS
        """
        return upload_file_to_ipfs(stix_file_path)
    def uploadModelFileToIPFS(self,model_file_path:str)->tuple[str,str]:
        """
            上传模型文件到IPFS
        """
        return upload_file_to_ipfs(model_file_path)
    def downloadStixFileFromIPFS(self,ipfs_hash:str)->tuple[str,str]:
        """
            从IPFS下载stix文件
        """
        return download_file_from_ipfs(ipfs_hash)
