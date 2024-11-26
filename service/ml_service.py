from db.tiny_db import get_tiny_db_instance
from ml.ml_model import start_model_process_task
from utils.file import check_file_by_hash
from env.global_var import getMlUploadFilePath
from ml.model_status import get_model_progress_status_by_id,get_model_record_by_id
from ml.model_status import get_model_progress_status_by_hash,get_model_record_by_hash
import threading
import uuid
class MLService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        # 自动生成请求 ID
    def generate_request_id(self):
        return str(uuid.uuid4())
    def get_upload_file_path_by_hash(self, hash):
        """
            根据文件的hash值,获取数据集文件路径
            param:
                hash: 数据集文件的hash值
            return:
                file_path: 数据集文件路径
        """
        return check_file_by_hash(getMlUploadFilePath(),hash)
    

    def createModelTask(self,source_file_hash:str,label_column:str)->bool:
        """
            创建模型任务(使用线程)
            param:
                - source_file_hash: 训练源文件的HASH
                - label_column: 标签列
            return:
                - request_id: 请求ID
        """
        
    
        # 根据文件hash获取文件路径
        source_file_path = self.get_upload_file_path_by_hash(source_file_hash)
        if source_file_path is None:
            return False
        
        request_id = self.generate_request_id()
        # 使用线程启动模型训练任务
        thread = threading.Thread(
            target=start_model_process_task,
            args=(request_id,source_file_hash, source_file_path, label_column)
        )
        thread.start()
            
        return True
    
    def getModelProgress(self, request_id: str) -> dict:
        """
        获取模型训练进度
        param:
            - request_id: 请求ID
        return:
            - dict: 训练进度记录
        """
        
        return get_model_progress_status_by_id(request_id)
    
    def getModelProgressByHash(self, source_file_hash: str) -> list:
        """
        根据源文件hash获取模型训练进度列表
        param:
            - source_file_hash: 源文件hash
        return:
            - list: 训练进度记录列表
        """
        return get_model_progress_status_by_hash(source_file_hash)
    
    def getModelRecord(self, request_id: str) -> dict:
        """
        获取模型记录
        param:
            - request_id: 请求ID
        return:
            - dict: 模型记录
        """
        return get_model_record_by_id(request_id)
    
    def getModelRecordsByHash(self, source_file_hash: str) -> list:
        """
        根据源文件hash获取模型记录列表
        param:
            - source_file_hash: 源文件hash
        return:
            - list: 模型记录列表
        """
        return get_model_record_by_hash(source_file_hash)
    
    

