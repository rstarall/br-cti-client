from db.tiny_db import get_tiny_db_instance
from data.traffic_data import get_traffic_data_features_name
from utils.file import check_file_by_hash
from env.global_var import getUploadFilePath,getOutputDirPath
import pandas as pd
from data.stix_process import start_process_dataset_to_stix
from utils.file import get_file_sha256_hash
from service.model.cti_model import cti_info_example,CTI_TYPE,CTI_TYPE_NAME,CTI_TRAFFIC_TYPE,TAGS_LIST,IOCS_LIST
from service.wallet_service import WalletService
from data.extensions_data import ips_to_location,ips_to_location_concurrent,ips_to_location_mock_random,ips_to_location_bulk
from env.global_var import getUploadChainDataPath
from utils.file import save_json_to_file,load_json_from_file
import time
import os
import threading
import random
import logging
wallet_service = WalletService()
class DataService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.stix_process_progress = {}
        self.cti_process_progress = {}
    def create_task_record(self,task_id,source_file_hash):
        """
            创建任务记录
            param:
                task_id: 任务ID(process_id)
                source_file_hash: 源文件hash值
            return:
                task_record: 任务记录
        """
        new_step_status = {
            "step":0, #文件上传step
            "status":"finished",
            "total_num":1
        }
        new_task_record = {
            "task_id":task_id,
            "source_file_hash":source_file_hash,
            "step_status":[new_step_status]
        }
        self.tiny_db.use_database("data_task_records").upsert_by_key_value("data_task_records",new_task_record,"source_file_hash",source_file_hash)
        return new_task_record
    
    def update_task_record(self,task_id,task_step=0,task_status="processing",total_num=0):
        """
            更新任务记录
            step: 
                0 - 文件上传step
                1 - stix转换step
                2 - cti处理step
                3 - 情报上链step
            param:
                - task_id: 任务ID
                - task_step: 任务步数
                - task_status: 任务状态
                - total_num: 总处理数
        """
        new_step_status = {
            "step":task_step,
            "status":task_status,
            "total_num":total_num
        }
        task_records = self.tiny_db.use_database("data_task_records").read_by_key_value("data_task_records","task_id",task_id)
        if task_records is not None:
            task_record = task_records[0]
            if task_record.get("step_status") is None:
                task_record["step_status"]=[new_step_status]
            else:
                if len(task_record["step_status"])>task_step:
                    task_record["step_status"][task_step] = new_step_status
                else:
                    task_record["step_status"].append(new_step_status)
            self.tiny_db.use_database("data_task_records").upsert_by_key_value("data_task_records",task_record,"task_id",task_id)
    
    def get_latest_task_record(self,source_file_hash):
        """
            获取最新任务记录
            param:
                source_file_hash: 源文件hash值
            return:
                latest_task_record: 最新任务记录
        """
        latest_task_record = self.tiny_db.use_database("data_task_records").read_sort_by_timestamp("data_task_records",field_name="source_file_hash",field_value=source_file_hash)
        if len(latest_task_record)>0:
            return latest_task_record[0]
        else:
            return None
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
    def process_data_to_stix(self,file_hash,stix_process_config):
        """
            处理数据集文件,并生成stix文件
            param:
                file_hash: 文件的hash值
                stix_process_config: 处理配置
            return:
                current_step: 当前步数
                total_step: 总步数(行数)
        """
        #根据file_hash获取文件路径
        file_path = self.get_upload_file_path_by_hash(file_hash)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.csv':
                # 尝试不同编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("无法以任何支持的编码读取CSV文件")
            elif file_ext == '.txt':
                df = pd.read_json(file_path,lines=True)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            raise
        
        #初始化处理配置
        #获取压缩率
        compress_rate = max(1, stix_process_config.get("stix_compress",1))  #确保压缩率最小为1
        #获取文件的行数
        total_step = max(1, df.shape[0]//compress_rate)  #确保总步数最小为1
        total_task_list = [i for i in range(total_step)]
        #处理进度保存到全局变量
        self.update_stix_process_progress(file_hash,0,total_step,total_task_list=total_task_list)

        #启动线程处理文件
        thread = threading.Thread(target=start_process_dataset_to_stix,args=(self,file_hash,stix_process_config))
        thread.start()
        return 0,total_step
    def get_stix_output_dir_path(self,file_hash):
        """
            获取stix输出文件夹路径

            param:
                - file_hash: 文件的hash值

            return:
                - stix_output_dir_path: stix输出文件夹路径
        """
        output_dir_path = getOutputDirPath() +"/"+ file_hash
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        return output_dir_path
        
    def update_stix_process_progress(self,file_hash,current_step=None,total_step=None,result=None,errors=None,current_task_id=None,total_task_list=None):
        """
            设置stix转换处理进度

            param:
                - file_hash: 文件的hash值
                - current_step: 当前步数
                - total_step: 总步数
                - result: 处理结果(如果处理已完成)   
                - current_task_id: 当前任务ID
                - total_task_list: 总任务列表

            return:
                - None
        """
        stix_process_progress = self.stix_process_progress.get(file_hash,{})
        if current_step is not None and total_step>0:
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
  
    def get_stix_process_progress(self,file_hash):
        """
            获取stix转换处理进度

            param:
                - file_hash: 文件的hash值

            return:
                - stix_process_progress: stix转换处理进度
        """
        stix_process_progress = self.stix_process_progress.get(file_hash,None)
        return stix_process_progress
    
    def get_history_abort_stix_process_progress(self,file_hash):
        """
            获取历史中止的stix转换处理进度 ,从全局变量中(内存)获取

            param:
                - file_hash: 文件的hash值

            return:
                - stix_process_progress: stix转换处理进度
        """
        stix_process_progress = self.stix_process_progress.get(file_hash,None)
        return stix_process_progress

    def save_local_stix_process_record(self,source_file_hash,stix_file_path,stix_info=None):
        """
            创建保存本地stix处理记录
            记录保存在tiny_db的stix_records表中
            同时保存stix_records json文件夹
            param:
                - source_file_hash: 源文件的hash值
                - stix_file_path: stix文件路径
                - stix_info: stix信息记录
        """
        new_stix_record_detail = {
            "source_file_hash":source_file_hash,
            "stix_file_path":"",
            "stix_file_size":0,#单位：字节
            "stix_file_hash":"",
            "stix_type":CTI_TYPE["TRAFFIC"],#默认设置为恶意流量
            "stix_type_name":CTI_TYPE_NAME[CTI_TYPE["TRAFFIC"]],
            "stix_tags":random.sample(list(TAGS_LIST.keys())[:-4],2),#随机两个标签
            "stix_iocs":random.sample(list(IOCS_LIST.keys()),2),#随机两个iocs
            "ioc_ips_map":{},
            "create_time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "onchain":False
        }
        #判断file_path是否存在
        if  os.path.exists(stix_file_path):
            new_stix_record_detail["stix_file_path"] = stix_file_path
            new_stix_record_detail["stix_file_size"] = os.path.getsize(stix_file_path)
        #处理stix_file_hash
        stix_file_hash = ""
        if "stix_data_hash" in stix_info:
            if stix_info["stix_data_hash"]!="":
                stix_file_hash = stix_info["stix_data_hash"]
            else:
                if os.path.exists(stix_file_path):
                    stix_file_hash = get_file_sha256_hash(stix_file_path)
        new_stix_record_detail["stix_file_hash"] = stix_file_hash
        #处理stix_type,stix_tags,stix_iocs
        if stix_info is not None:
            if stix_info.get("stix_type") is not None:
                new_stix_record_detail["stix_type"] = stix_info["stix_type"]
            if stix_info.get("stix_tags") is not None:
                new_stix_record_detail["stix_tags"] = stix_info["stix_tags"]
            if stix_info.get("stix_iocs") is not None:
                new_stix_record_detail["stix_iocs"] = stix_info["stix_iocs"]
        #处理ioc_ips_map
        if stix_info.get("ioc_ips_map") is not None:
            new_stix_record_detail["ioc_ips_map"] = stix_info["ioc_ips_map"]
        #保存stix_record_info json文件
        stix_record_file_path = ""
        data_client_path = self.tiny_db.get_data_client_path()
        if stix_file_hash!="":
            stix_record_file_path = data_client_path+"/stix_records/"+source_file_hash+"/"+stix_file_hash+".json"
            save_json_to_file(stix_record_file_path,new_stix_record_detail)
        #保存摘要信息到tiny_db
        stix_record = {
            "source_file_hash":source_file_hash,
            "stix_file_hash":stix_file_hash,
            "stix_file_path":stix_record_file_path,
            "create_time":new_stix_record_detail["create_time"]
        }
        self.tiny_db.use_database("stix_records").upsert_by_key_value("stix_records",stix_record,"stix_file_hash",stix_file_hash)
        
        return new_stix_record_detail
    
    def get_local_stix_records(self,source_file_hash,page=1,page_size=15,all=False):
        """
            获取本地stix记录表,支持分页

            param:
                - source_file_hash: 源文件的hash值
                - page: 页码
                - page_size: 每页大小
                - all: 是否获取所有记录

            return:
                - stix_records_detail_list: stix记录详情列表
        """
        
        stix_records_list = self.tiny_db.use_database("stix_records").read_sort_by_timestamp("stix_records",field_name="source_file_hash",field_value=source_file_hash)
        if not all:
            total_count = len(stix_records_list)
            start_index = (page-1)*page_size #计算起始索引
            end_index = min(start_index+page_size,total_count) #计算结束索引
            stix_records_list = stix_records_list[start_index:end_index]
        #读取stix_record_info json文件
        stix_records_detail_list = []
        data_client_path = self.tiny_db.get_data_client_path()
        for stix_record in stix_records_list:
            stix_record_file_path = data_client_path+"/stix_records/"+source_file_hash+"/"+stix_record["stix_file_hash"]+".json"
            #判断文件是否存在
            if os.path.exists(stix_record_file_path):
                stix_records_detail_list.append(load_json_from_file(stix_record_file_path))
        return stix_records_detail_list
    
    def get_local_stix_file_by_hash(self,source_file_hash,stix_file_hash):
        """
            根据stix文件的hash值获取本地stix文件路径

            param:
                - source_file_hash: 源文件的hash值
                - stix_file_hash: stix文件的hash值

            return:
                - stix_data: stix数据,str类型
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
                - source_file_hash: 源文件的hash值
                - current_step: 当前步数
                - total_step: 总步数
                - current_task_id: 当前任务ID
                - total_task_list: 总任务列表
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
                if current_task_id in self.cti_process_progress[source_file_hash]["total_task_list"]:
                    self.cti_process_progress[source_file_hash]["total_task_list"].remove(current_task_id)

    def get_cti_process_progress(self,source_file_hash):
        """
            获取情报处理进度
            :param
                task_id: 任务ID(source_file_hash)
            :return
                cti_process_progress: 情报处理进度
        """
        cti_process_progress = self.cti_process_progress.get(source_file_hash,None)
        return cti_process_progress
    
    def get_history_abort_cti_process_progress(self,source_file_hash):
        """
            获取历史中止的情报处理进度 ,从全局变量中(内存)获取
        """
        cti_process_progress = self.cti_process_progress.get(source_file_hash,None)
        return cti_process_progress
    
    def start_create_local_cti_records_by_hash(self,source_file_hash,cti_config):
        """
            启动线程创建本地情报记录
            :param
                source_file_hash: 源文件的hash值
                cti_config: 情报配置
        """
        thread = threading.Thread(target=self.create_local_cti_records_by_hash,args=(source_file_hash,cti_config))
        thread.start()
        
    def create_local_cti_records_by_hash(self,source_file_hash,cti_config):
        """
            根据source_file_hash创建本地情报记录
            :param
                source_file_hash: 源文件的hash值
                cti_config: 情报配置
            :return
                new_cti_record_list: 新创建的情报记录列表
        """
        #查询数据库
        stix_info_list = self.get_local_stix_records(source_file_hash,all=True)
        new_cti_record_list = []
        if len(stix_info_list)>0:
            #初始化情报处理进度
            total_task_list = [stix_info["stix_file_hash"] for stix_info in stix_info_list]
            self.update_cti_process_progress(source_file_hash,0,len(stix_info_list),total_task_list=total_task_list)
            for index,stix_info in enumerate(stix_info_list):
                try:
                    new_cti_record = self.create_local_cti_record(source_file_hash,stix_info["stix_file_path"],stix_info,cti_config)
                except Exception as e:
                    logging.error(f"create_local_cti_record error:{e}")
                new_cti_record_list.append(new_cti_record)
                #更新情报处理进度
                self.update_cti_process_progress(source_file_hash,len(new_cti_record_list),len(stix_info_list),current_task_id=stix_info["stix_file_hash"])
            return new_cti_record_list
        else:
            return []
        

    def create_local_cti_record(self,source_file_hash,stix_file_path,stix_info,cti_config):
        """
            创建保存本地情报记录(source_file_hash->{cti_id,create_time})
            保存cti文件(上链文件夹中)
            param:
                - source_file_hash: 源文件的hash值
                - stix_file_path: stix文件路径
                - stix_info: stix信息记录
                - cti_config: 情报配置
        """
        stix_file_hash = get_file_sha256_hash(stix_file_path)
        new_cti_info_record = {
            "cti_hash": stix_file_hash,
            "creator_user_id": wallet_service.checkUserAccountExist(),
            "cti_type": cti_config.get("cti_type", stix_info["stix_type"]),
            "cti_traffic_type": CTI_TRAFFIC_TYPE["5G"] if stix_info["stix_type"]==CTI_TYPE["TRAFFIC"] else 0, #注意类型
            "open_source": cti_config.get("open_source", 1),
            "tags": stix_info["stix_tags"],#使用stix的标签
            "iocs": stix_info["stix_iocs"],#使用stix的iocs
            "stix_data": stix_file_path, #暂时记录为stix文件路径
            "description": cti_config.get("description", ""),
            "data_size": os.path.getsize(stix_file_path),
            "data_hash": stix_file_hash,
            "ipfs_hash": "",
            "value": cti_config.get("value", 10)
        }
        #处理create_time
        new_cti_info_record["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #处理统计信息
        satistic_info={}
        if "ioc_ips_map" in stix_info:
            satistic_info["ioc_ips_map"] = stix_info["ioc_ips_map"]
            #处理ioc_locations_map(ip->地理位置)
            #ip转地理位置
            print(f"正在处理ioc_ips_map:{len(stix_info['ioc_ips_map'].keys())}")
            try:
                ip_location_map,ip_location_info_map,location_num_map,errors = self.process_ips_to_locations(stix_info["ioc_ips_map"])
                satistic_info["ips_locations_map"] = ip_location_map
                satistic_info["ips_locations_info_map"] = ip_location_info_map
                satistic_info["ioc_locations_map"] = location_num_map
            except Exception as e:
                logging.error(f"process_ips_to_locations error:{e}")
        #保存统计信息
        self.save_cti_statistic_info(source_file_hash,new_cti_info_record["cti_hash"],satistic_info)
        #保存到数据库文件夹中
        cti_record_detail_path = ""
        data_client_path = self.tiny_db.get_data_client_path()
        if new_cti_info_record["cti_hash"]!="":
            cti_record_detail_path = data_client_path+"/cti_records/"+source_file_hash+"/"+new_cti_info_record["cti_hash"]+".json"
            save_json_to_file(cti_record_detail_path,new_cti_info_record)
        #保存摘要
        cti_record = {
            "source_file_hash":source_file_hash,
            "cti_hash":new_cti_info_record["cti_hash"],
            "cti_file_path":cti_record_detail_path,
            "create_time":new_cti_info_record["create_time"]
        }
        self.tiny_db.use_database("cti_records").upsert_by_key_value("cti_records",cti_record,"cti_hash",new_cti_info_record["cti_hash"])
        
        return new_cti_info_record
    def save_cti_statistic_info(self,source_file_hash,cti_hash:str,statistic_info:dict):
        """
            保存情报统计信息
            param:
                - source_file_hash: 源文件的hash值
                - cti_hash: 情报hash值(stix的hash值)
                - statistic_info: 统计信息
        """
        #保存到数据库文件夹中
        cti_record_detail_path = ""
        data_client_path = self.tiny_db.get_data_client_path()
        if cti_hash!=None:
            cti_record_detail_path = data_client_path+"/cti_records/"+source_file_hash+"/"+cti_hash+"_statistic_info.json"
            save_json_to_file(cti_record_detail_path,statistic_info)
    def get_cti_statistic_info_path(self,source_file_hash,cti_hash):
        """
            获取情报统计信息路径
            param:
                - source_file_hash: 源文件的hash值
                - cti_hash: 情报hash值(stix的hash值)
        """
        data_client_path = self.tiny_db.get_data_client_path()
        return data_client_path+"/cti_records/"+source_file_hash+"/"+cti_hash+"_statistic_info.json"
    def process_ips_to_locations(self,ips_map):
        """
            处理ip->地理位置
            param:
                - ips_map: ip字典(ip->ip出现数量)

            return:
                - ip_location_map: ip地理位置字典(ip->地理位置)
                - ip_location_info_map: ip地理位置信息字典(ip->地理位置详细信息)
                - location_num_map: 地理位置出现数量字典(地理位置->位置出现数量)
                - errors: 错误信息列表
        """
        #ip_location_map,location_num_map,errors = ips_to_location(ips_map)
        #使用批量查询API处理(每次30个)
        ip_location_map,ip_location_info_map,location_num_map,errors = ips_to_location(ips_map)
        return ip_location_map,ip_location_info_map,location_num_map,errors
    
    def get_local_cti_record_by_id(self,source_file_hash,cti_id):
        """
            根据cti_id获取本地情报记录
            param:
                - source_file_hash: 源文件的hash值
                - cti_id: 情报ID
            return:
                - cti_record: 情报记录
        """
        cti_record_file_path = self.tiny_db.get_data_client_path()+"/cti_records/"+source_file_hash+"/"+cti_id+".json"
        if os.path.exists(cti_record_file_path):
            return load_json_from_file(cti_record_file_path)
        else:
            return None
        
    def get_local_cti_records_detail_list(self,source_file_hash):
        """
            根据source_file_hash获取本地情报记录
        """
        file_path_list = self.get_local_cti_records_file_path_list(source_file_hash,all=True)
        cti_records_detail_list = []
        for file_path in file_path_list:
            #判断文件是否存在
            if os.path.exists(file_path):
                cti_records_detail_list.append(load_json_from_file(file_path))
        return cti_records_detail_list
    
    def get_local_cti_records_file_path_list(self,source_file_hash,page=1,page_size=15,all=False):
        """
            获取本地情报记录表,支持分页
            
            param:
                - source_file_hash: 源文件的hash值
                - page: 页码
                - page_size: 每页大小
                - all: 是否获取所有记录
                
            return:
                - cti_records_detail_list: 情报记录详情列表
        """
        cti_records_list = self.tiny_db.use_database("cti_records").read_sort_by_timestamp("cti_records",field_name="source_file_hash",field_value=source_file_hash)
        if not all:
            total_count = len(cti_records_list)
            start_index = (page-1)*page_size #计算起始索引
            end_index = min(start_index+page_size,total_count) #计算结束索引
            cti_records_list = cti_records_list[start_index:end_index]
        #读取cti_record_info json文件
        cti_records_file_path_list = []
        for cti_record in cti_records_list:
            cti_records_file_path_list.append(cti_record["cti_file_path"])
        return cti_records_file_path_list
        
