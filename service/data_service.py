from db.tiny_db import get_tiny_db_instance
from data.traffic_data import get_traffic_data_features_name
from utils.file import check_file_by_hash
from env.global_var import getUploadFilePath,getOutputDirPath
import pandas as pd
from data.stix_process import start_process_dataset_to_stix
import os
import threading
class DataService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.stix_process_progress = {}
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
        total_step = df.shape[0]
        #处理进度保存到全局变量
        self.update_stix_process_progress(file_hash,0,total_step)

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
        
    def update_stix_process_progress(self,file_hash,current_step=None,total_step=None,result=None,errors=None):
        """
            设置stix转换处理进度
            param:
                file_hash: 文件的hash值
                current_step: 当前步数
                total_step: 总步数
                result: 处理结果(如果处理已完成)   
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
        self.stix_process_progress[file_hash] = stix_process_progress


    def get_stix_process_progress(self,file_hash):
        """
            获取stix转换处理进度
            param:
                file_hash: 文件的hash值
            return:
                stix_process_progress: stix转换处理进度
        """
        return self.stix_process_progress.get(file_hash,None)

