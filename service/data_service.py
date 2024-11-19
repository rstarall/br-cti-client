from db.tiny_db import get_tiny_db_instance
from data.traffic_data import get_traffic_data_features_name
from utils.file import check_file_by_hash
from env.global_var import getUploadFilePath
import pandas as pd
class DataService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        self.stix_process_progress = {}
    def processCsvToStix(self, csv_path):
        pass
    def saveFileToLocal(self, file_path):
        pass
    def getFilePathByHash(self, hash):
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
            file_path = self.getFilePathByHash(file_hash)
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
        file_path = self.getFilePathByHash(file_hash)
        #读取文件
        df = pd.read_csv(file_path)
        #获取文件的行数
        total_step = df.shape[0]
        #处理进度保存到全局变量
        self.set_stix_process_progress(file_hash,0,0,total_step)

        #启动线程处理文件
        # thread = threading.Thread(target=self.process_data_to_stix_thread,args=(file_hash,process_config,df))
        # thread.start()
        return 0,total_step

        
    def set_stix_process_progress(self,file_hash,progress,current_step=None,total_step=None):
        """
            设置stix转换处理进度
        """
        self.stix_process_progress[file_hash] = {
            "progress":progress,
            "current_step":current_step,
            "total_step":total_step
        }
    def get_stix_process_progress(self,file_hash):
        """
            获取stix转换处理进度
        """
        return self.stix_process_progress.get(file_hash,{})

