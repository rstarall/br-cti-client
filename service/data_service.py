from db.tiny_db import get_tiny_db_instance
from data.traffic_data import get_traffic_data_features_name
from utils.file import check_file_by_hash
from env.global_var import getUploadFilePath,getOutputDirPath
import pandas as pd
from data.stix_process import start_process_dataset_to_stix
from utils.file import get_file_sha256_hash
from service.model.cti_model import cti_info_example,ATTACK_TYPE,ATTACK_TYPE_NAME,CTI_TRAFFIC_TYPE,TAGS_LIST,IOCS_LIST
from service.wallet_service import WalletService
from data.extensions_data import ips_to_location
from env.global_var import getUploadChainDataPath
from utils.file import save_json_to_file
import time
import os
import threading
import random
wallet_service = WalletService()
class DataService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.stix_process_progress = {}
        self.cti_process_progress = {}
        
    def get_upload_file_path_by_hash(self, hash):
        """
            根据文件的hash值,获取文件路径
            param:
                hash: 文件的hash值
            return:
                file_path: 文件路径
        """
        return check_file_by_hash(getUploadFilePath(),hash)
    def get_traffic_data_features_name(self, file_hash):
        """
            根据文件的hash值,获取数据集文件的特征名称
            param:
                file_hash: 文件的hash值
            return:
                features_name: 特征名称,
                error: 错误信息,如果成功则为None
        """
        try:
            file_path = self.get_upload_file_path_by_hash(file_hash)
            return get_traffic_data_features_name(file_path),None
        except Exception as e:
            return None,str(e)
    def process_data_to_stix(self,file_hash,process_config):
        """
            处理数据集文件,并生成stix文件
            param:
                file_hash: 文件的hash值
                process_config: 处理配置
            return:
                current_step: 当前步数
                total_step: 总步数(行数)
        """
        #根据file_hash获取文件路径
        file_path = self.get_upload_file_path_by_hash(file_hash)
        #读取文件
        df = pd.read_csv(file_path)
        #获取文件的行数
        compress_rate = process_config.get("stix_compress",500)
        total_step = df.shape[0]//compress_rate
        total_task_list = [i for i in range(total_step)]
        #处理进度保存到全局变量
        self.update_stix_process_progress(file_hash,0,total_step,total_task_list=total_task_list)

        #启动线程处理文件
        thread = threading.Thread(target=start_process_dataset_to_stix,args=(self,file_hash,process_config))
        thread.start()
        return 0,total_step
    def get_stix_output_dir_path(self,file_hash):
        """
            获取stix输出文件夹路径

            param:
                file_hash: 文件的hash值
            return:
                stix_output_dir_path: stix输出文件夹路径
        """
        output_dir_path = getOutputDirPath() +"/"+ file_hash
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        return output_dir_path
        
    def update_stix_process_progress(self,file_hash,current_step=None,total_step=None,result=None,errors=None,current_task_id=None,total_task_list=None):
        """
            设置stix转换处理进度
            param:
                file_hash: 文件的hash值
                current_step: 当前步数
                total_step: 总步数
                result: 处理结果(如果处理已完成)   
                current_task_id: 当前任务ID
                total_task_list: 总任务列表
            return:
                None
        """
        stix_process_progress = self.stix_process_progress.get(file_hash,{})
        if current_step is not None and total_step is not None:
            stix_process_progress["progress"] = min(int((current_step/total_step)*100),100) 
            stix_process_progress["current_step"] = current_step
            stix_process_progress["total_step"] = total_step
        if result is not None:
            stix_process_progress["result"] = result
        if errors is not None:
            stix_process_progress["errors"] = errors
        if total_task_list is not None:
            #初始化总任务列表
            total_task_list = list(total_task_list)
            stix_process_progress["total_task_list"] = total_task_list
        if current_task_id is not None:
            stix_process_progress["current_task_id"] = current_task_id
            #移出完成任务
            if stix_process_progress["total_task_list"] is not None:
                if current_task_id in stix_process_progress["total_task_list"]:
                    stix_process_progress["total_task_list"].remove(current_task_id)
        
        self.stix_process_progress[file_hash] = stix_process_progress
        #保存到tiny_db
        self.tiny_db.use_database("stix_process_progress").upsert_by_key_value("stix_process_progress",stix_process_progress,"file_hash",file_hash)

    def get_stix_process_progress(self,file_hash):
        """
            获取stix转换处理进度
            param:
                file_hash: 文件的hash值
            return:
                stix_process_progress: stix转换处理进度
        """
        stix_process_progress = self.stix_process_progress.get(file_hash,None)
        if stix_process_progress is None:
            #从tiny_db中获取
            stix_process_progress = self.tiny_db.use_database("stix_process_progress").read_by_key_value("stix_process_progress",field_name="file_hash",field_value=file_hash)
            if stix_process_progress is not None:
                self.stix_process_progress[file_hash] = stix_process_progress
        return stix_process_progress
    
    def get_history_abort_stix_process_progress(self,file_hash):
        """
            获取历史中止的stix转换处理进度 ,从tiny_db中获取
            param:
                file_hash: 文件的hash值
            return:
                stix_process_progress: stix转换处理进度
        """
        #从tiny_db中获取
        stix_process_progress = self.tiny_db.use_database("stix_process_progress").read_by_key_value("stix_process_progress",field_name="file_hash",field_value=file_hash)
        if stix_process_progress is not None:
            self.stix_process_progress[file_hash] = stix_process_progress
        return stix_process_progress

    def save_local_stix_process_record(self,source_file_hash,stix_file_path,stix_info=None):
        """
            创建保存本地stix处理记录
            保存在tiny_db的stix_info_records表中
            param:
                source_file_hash: 源文件的hash值
                stix_file_path: stix文件路径
                stix_info: stix信息记录
        """
        new_stix_info_record = {
            "source_file_hash":source_file_hash,
            "stix_file_path":"",
            "stix_file_size":0,#单位：字节
            "stix_file_hash":"",
            "stix_type":ATTACK_TYPE["TRAFFIC"],#默认设置为恶意流量
            "stix_type_name":ATTACK_TYPE_NAME[ATTACK_TYPE["TRAFFIC"]],
            "stix_tags":random.sample(TAGS_LIST,2),#随机两个标签
            "stix_iocs":random.sample(IOCS_LIST,2),#随机两个iocs
            "ioc_ips_map":{},
            "create_time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "onchain":False
        }
        #判断file_path是否存在
        if  os.path.exists(stix_file_path):
            new_stix_info_record["stix_file_path"] = stix_file_path
            new_stix_info_record["stix_file_size"] = os.path.getsize(stix_file_path)
        #处理stix_file_hash
        if "stix_data_hash" in stix_info:
            if stix_info["stix_data_hash"]!="":
                new_stix_info_record["stix_file_hash"] = stix_info["stix_data_hash"]
            else:
                if os.path.exists(stix_file_path):
                    new_stix_info_record["stix_file_hash"] = get_file_sha256_hash(stix_file_path)

        #处理stix_type,stix_tags,stix_iocs
        if stix_info is not None:
            if "stix_type" in stix_info:
                new_stix_info_record["stix_type"] = stix_info["stix_type"]
            if "stix_tags" in stix_info:
                new_stix_info_record["stix_tags"] = stix_info["stix_tags"]
            if "stix_iocs" in stix_info:
                new_stix_info_record["stix_iocs"] = stix_info["stix_iocs"]
        #处理ioc_ips_map
        if "ioc_ips_map" in stix_info:
            new_stix_info_record["ioc_ips_map"] = stix_info["ioc_ips_map"]

        
        #更新或插入数据(stix处理信息表)
        self.tiny_db.use_database("stix_records").upsert_by_key_value("stix_info_records",new_stix_info_record,"file_hash",source_file_hash)
        return new_stix_info_record
    
    def get_local_stix_records(self,file_hash,page=1,page_size=15,all=False):
        """
            获取本地stix记录表,支持分页
            param:
                file_hash: 源文件的hash值
                page: 页码
                page_size: 每页大小
                all: 是否获取所有记录
            return:
                records: 记录列表
        """
        
        stix_records_list = self.tiny_db.use_database("stix_records").read_sort_by_timestamp("stix_info_records",field_name="file_hash",field_value=file_hash)
        print("get_local_stix_records results:",stix_records_list)
        if not all:
            total_count = len(stix_records_list)
            start_index = (page-1)*page_size #计算起始索引
            end_index = min(start_index+page_size,total_count) #计算结束索引
            return stix_records_list[start_index:end_index]
        else:
            return stix_records_list
    
    def get_local_stix_file_by_hash(self,source_file_hash,stix_file_hash):
        """
            根据stix文件的hash值获取本地stix文件路径
            param:
                source_file_hash: 源文件的hash值
                stix_file_hash: stix文件的hash值
            return:
                stix_data: stix数据,str类型
        """
        stix_file_path = getOutputDirPath()+"/"+source_file_hash+"/"+stix_file_hash+".jsonl"
        if os.path.exists(stix_file_path):
            #读取stix文件
            with open(stix_file_path,"r") as fp:
                stix_data = fp.read()
            return stix_data
        else:
            return None
    def update_cti_process_progress(self,source_file_hash,current_step=None,total_step=None,current_task_id=None,total_task_list=None):
        """
            更新情报处理进度
            param:
                source_file_hash: 源文件的hash值
                current_step: 当前步数
                total_step: 总步数
                current_task_id: 当前任务ID
                total_task_list: 总任务列表
        """
        if total_task_list is not None:
            #初始化总任务列表
            total_task_list = list(total_task_list)
            self.cti_process_progress[source_file_hash] = {
                "progress":min(int((current_step/total_step)*100),100),
                "current_step":current_step,
                "total_step":total_step,
                "total_task_list":total_task_list,
                "current_task_id":current_task_id
            }
        else:
            #更新进度
            self.cti_process_progress[source_file_hash]["progress"] = min(int((current_step/total_step)*100),100)
            self.cti_process_progress[source_file_hash]["current_step"] = current_step
            self.cti_process_progress[source_file_hash]["total_step"] = total_step
            self.cti_process_progress[source_file_hash]["current_task_id"] = current_task_id
            #移出完成任务
            if current_task_id is not None:
                self.cti_process_progress[source_file_hash]["total_task_list"].remove(current_task_id)
        #保存到tiny_db
        self.tiny_db.use_database("cti_process_progress").upsert_by_key_value("cti_process_progress",self.cti_process_progress[source_file_hash],"source_file_hash",source_file_hash)

    def get_cti_process_progress(self,source_file_hash):
        """
            获取情报处理进度
            param:
                task_id: 任务ID(source_file_hash)
            return:
                cti_process_progress: 情报处理进度
        """
        cti_process_progress = self.cti_process_progress.get(source_file_hash,None)
        if cti_process_progress is  None:
            #从tiny_db中获取
            progress = self.tiny_db.use_database("cti_process_progress").read_by_key_value("cti_process_progress",field_name="task_id",field_value=task_id)
            if progress is not None:
                self.cti_process_progress[source_file_hash] = progress
        return cti_process_progress
    
    def get_history_abort_cti_process_progress(self,source_file_hash):
        """
            获取历史中止的情报处理进度 ,从tiny_db中获取
        """
        cti_process_progress = self.tiny_db.use_database("cti_process_progress").read_by_key_value("cti_process_progress",field_name="source_file_hash",field_value=source_file_hash)
        if cti_process_progress is not None:
            self.cti_process_progress[source_file_hash] = cti_process_progress
        return cti_process_progress
    def start_create_local_cti_records_by_hash(self,source_file_hash):
        """
            启动线程创建本地情报记录
            param:
                source_file_hash: 源文件的hash值
        """
        thread = threading.Thread(target=self.create_local_cti_records_by_hash,args=(source_file_hash,))
        thread.start()
        
    def create_local_cti_records_by_hash(self,source_file_hash):
        """
            根据source_file_hash创建本地情报记录

            param:
                source_file_hash: 源文件的hash值
            return:
                new_cti_record_list: 新创建的情报记录列表
        """
        #查询数据库
        stix_info_list = self.tiny_db.use_database("stix_records").read_by_key_value("stix_info_records",field_name="file_hash",field_value=source_file_hash)
        new_cti_record_list = []
        if len(stix_info_list)>0:
            #初始化情报处理进度
            total_task_list = [stix_info["stix_file_hash"] for stix_info in stix_info_list]
            self.update_cti_process_progress(source_file_hash,0,len(stix_info_list),total_task_list=total_task_list)
            for stix_info in stix_info_list:
                new_cti_record = self.save_local_cti_record(stix_info["stix_file_path"],stix_info)
                new_cti_record_list.append(new_cti_record)
                #更新情报处理进度
                self.update_cti_process_progress(source_file_hash,len(new_cti_record_list),len(stix_info_list),current_task_id=stix_info["stix_file_hash"])
            return new_cti_record_list
        else:
            return []
        

    def save_local_cti_record(self,source_file_hash,stix_file_path,stix_info):
        """
            创建保存本地情报记录
            保存在tiny_db的cti_info_records表中
            param:
                source_file_hash: 源文件的hash值
                stix_file_path: stix文件路径
                stix_info: stix信息记录
        """
        new_cti_info_record = cti_info_example.copy()
        #获取情报ID
        new_cti_info_record["cti_id"] = get_file_sha256_hash(stix_file_path)
        #获取用户钱包ID
        new_cti_info_record["creator_user_id"] = wallet_service.checkUserAccountExist()
        #处理cti_type
        new_cti_info_record["cti_type"] = stix_info["stix_type"]
        #处理cti_traffic_type
        new_cti_info_record["cti_traffic_type"] = ""
        if stix_info["stix_type"]==ATTACK_TYPE["TRAFFIC"]:
            new_cti_info_record["cti_traffic_type"] = CTI_TRAFFIC_TYPE["5G"] #默认设置为5G攻击流量
        #处理open_source
        new_cti_info_record["open_source"] = 1 #默认设置为开源情报
        #处理tags
        new_cti_info_record["tags"] = stix_info["stix_tags"]
        #处理iocs
        new_cti_info_record["iocs"] = stix_info["stix_iocs"]
        #处理stix_data
        new_cti_info_record["stix_data"] = "" #默认不上传stix情报，上传到IPFS
        #处理description
        new_cti_info_record["description"] = "" #默认描述为空
        #处理data_size
        new_cti_info_record["data_size"] = os.path.getsize(stix_file_path)
        #处理data_hash
        new_cti_info_record["data_hash"] = get_file_sha256_hash(stix_file_path)
        #处理ipfs_hash
        new_cti_info_record["ipfs_hash"] = "" #默认IPFS哈希为空
        #处理value
        new_cti_info_record["value"] = 0 #默认价值为0(开源)
        #处理create_time
        new_cti_info_record["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #处理统计信息
        new_cti_info_record["satistic_info"] = {}
        if "ioc_ips_map" in stix_info:
            new_cti_info_record["satistic_info"]["ioc_ips_map"] = stix_info["ioc_ips_map"]
            #处理ioc_locations_map(ip->地理位置)
            #ip转地理位置
            ip_location_map,location_num_map = ips_to_location(stix_info["ioc_ips_map"])
            new_cti_info_record["satistic_info"]["ips_locations_map"] = ip_location_map
            new_cti_info_record["satistic_info"]["ioc_locations_map"] = location_num_map

        #保存到上链数据文件夹
        chain_data_file_path = getUploadChainDataPath()+"/"+source_file_hash+"/"+new_cti_info_record["cti_id"]+".json"
        save_json_to_file(chain_data_file_path,new_cti_info_record)
        #保存到tiny_db
        tiny_db = get_tiny_db_instance()
        #更新或插入数据(cti处理信息表)
        tiny_db.upsert_by_key_value("cti_info_records",new_cti_info_record,"cti_id",new_cti_info_record["cti_id"])
        return new_cti_info_record
    
    
