from db.tiny_db import get_tiny_db_instance
from ml.ml_model import start_model_process_task
from utils.file import check_file_by_hash
from env.global_var import getMlUploadFilePath,getMlDownloadFilePath
from ml.model_status import get_model_progress_status_by_id,get_model_record_by_request_id
from ml.model_status import get_model_progress_status_by_hash,get_model_record_by_hash,get_model_record_by_hash_and_hash
from ml.model_progress import get_train_progress_by_id
from data.traffic_data import get_feature_list
from utils.file import save_json_to_file,load_json_from_file
from blockchain.ipfs.ipfs import download_file_with_progress
import threading
import uuid
import os
import logging
import base64

class MLService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
        # 自动生成请求 ID
    def generate_request_id(self):
        return str(uuid.uuid4())
    
    def get_data_source_file_path_by_hash(self,hash):
        """
            根据文件的hash值,获取文件路径
            return:
                file_path: 文件路径
                error: 错误信息
        """
        #先检测上传文件夹
        file_path = check_file_by_hash(getMlUploadFilePath(),hash)
        if file_path is None:
            #检查下载文件夹
            return check_file_by_hash(getMlDownloadFilePath(),hash)
        return file_path
    
    def get_upload_file_path_by_hash(self, hash):
        """
            根据文件的hash值,获取数据集文件路径
            param:
                hash: 数据集文件的hash值
            return:
                file_path: 数据集文件路径
        """
        return check_file_by_hash(getMlUploadFilePath(),hash)
    
    def download_file_from_ipfs_by_hash(self,data_source_hash,ipfs_hash):
        """
            根据文件的hash值,从IPFS下载文件
            使用线程并监听进度
            param:
                data_source_hash: 数据源文件hash
                ipfs_hash: IPFS文件hash
            return:
                file_info: 文件信息
                error: 错误信息
        """
        file_info = {
            'save_path': "",
            'file_name': "",
            'file_size': 0,
            'file_ext': ''
        }
        def progress_callback(received, total):
            progress = {
                'received_bytes': received,
                'total_bytes': total,
                'progress': round(received / total * 100, 2) if total > 0 else 0
            }
            self.save_download_progress(data_source_hash, progress)
            
        save_path = getMlDownloadFilePath()
        #检测文件是否存在
        exit_file_path = check_file_by_hash(save_path,data_source_hash)
        if exit_file_path is not None:
            file_size = os.path.getsize(exit_file_path)
            progress_callback(file_size,file_size)
            file_info['save_path'] = exit_file_path
            file_info['file_size'] = file_size
            file_info['file_ext'] = os.path.splitext(exit_file_path)[1] if exit_file_path else ''
            file_info['file_name'] = os.path.basename(exit_file_path)
            return file_info,None

        return download_file_with_progress(data_source_hash,ipfs_hash, save_path, progress_callback)
    
    def save_download_progress(self,data_source_hash,progress):
        """
            保存下载进度
            param:
                data_source_hash: 数据源文件hash
                progress: 进度信息
        """
        try:
            data = {
                'file_hash': data_source_hash,
                **progress
            }
            self.tiny_db.use_database('ml_download_progress').upsert_by_key_value('progress', data, 'file_hash', data_source_hash)
        except Exception as e:
            logging.error(f"保存下载进度失败: {str(e)}")

    def get_download_progress(self,data_source_hash):
        """
            获取下载进度
            param:
                data_source_hash: 数据源文件hash
            return:
                progress: 进度信息
        """
        result = self.tiny_db.use_database('ml_download_progress').read_by_key_value('progress', 'file_hash', data_source_hash)
        if result and len(result) > 0:
            return result[0].get('progress')
        return None

    def get_download_file_path_by_hash(self,hash):
        """
            根据文件的hash值,获取下载文件路径
        """
        return check_file_by_hash(getMlDownloadFilePath(),hash)
    

    def get_feature_list(self, file_hash):
        """
            根据文件的hash值,获取数据集文件的特征名称
            param:
                file_hash: 文件的hash值
            return:
                features_name: 特征名称,
                error: 错误信息,如果成功则为None
        """
        try:
            file_path = self.get_data_source_file_path_by_hash(file_hash)
            if file_path is None:
                return None, "文件不存在:"+file_hash
            return get_feature_list(file_path), None
        except Exception as e:
            return None, str(e)

    def createModelTask(self,source_file_hash:str,label_column:str,cti_id=None)->bool:
        """
            创建模型任务(使用线程)
            param:
                - source_file_hash: 训练源文件的HASH
                - label_column: 标签列
                - cti_id: CTI的ID
            return:
                - request_id: 请求ID
                - bool: 是否成功
        """
        
    
        # 根据文件hash获取文件路径
        source_file_path = self.get_data_source_file_path_by_hash(source_file_hash)
        if source_file_path is None:
            return None,False
        
        request_id = self.generate_request_id()
        # 使用线程启动模型训练任务
        thread = threading.Thread(
            target=start_model_process_task,
            args=(request_id,source_file_hash, source_file_path, label_column,cti_id)
        )
        thread.start()
            
        return request_id,True
    
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
    
    def getTrainProgressDetailById(self,request_id:str)->dict:
        """
            根据请求ID获取训练过程的详细信息
            param:
                - request_id: 请求ID
            return:
                - dict: 训练过程的详细信息
        """
        return get_train_progress_by_id(request_id)
    
    def getModelRecordByRequestId(self, request_id: str) -> dict:
        """
        获取模型记录
        param:
            - request_id: 请求ID
        return:
            - dict: 模型记录
        """
        return get_model_record_by_request_id(request_id)
    
    def getModelRecordsBySourceFileHash(self, source_file_hash: str) -> list:
        """
        根据源文件hash获取模型记录列表
        param:
            - source_file_hash: 源文件hash
        return:
            - list: 模型记录列表
        """
        return get_model_record_by_hash(source_file_hash)
    
    def getModelRecordByHashAndHash(self,source_file_hash:str,model_hash:str)->dict:
        """
            根据源文件hash和模型hash获取模型记录
            param:
                - source_file_hash: 训练源文件的HASH
                - model_hash: 模型hash
            return:
                - record: 记录
        """
        return get_model_record_by_hash_and_hash(source_file_hash,model_hash)
    
    def getModelUpchainRecordsList(self,source_file_hash:str)->list:
        """
            根据source_file_hash获取本地模型上链记录列表
        """
        model_record_list = self.getModelRecordsBySourceFileHash(source_file_hash)
        model_records_detail_list = []
        for model_record in model_record_list:
            model_info = model_record.get("model_info",{})
            model_hash = model_info.get("model_hash","")
            #判断文件是否存在
            if os.path.exists(self.getModelUpchainInfoFilePath(source_file_hash,model_hash)):
                model_records_detail_list.append(load_json_from_file(self.getModelUpchainInfoFilePath(source_file_hash,model_hash)))
        return model_records_detail_list
    
    def getModelUpchainInfoFilePath(self,source_file_hash:str,model_hash:str)->str:
        """
            获取模型上链信息文件路径
        """
        return f"{self.tiny_db.get_ml_client_path()}/model_records/{source_file_hash}/{model_hash}.json"
    
    def createModelUpchainInfoBySourceFileHash(self,source_file_hash:str,model_info_config:str)->bool:
        """
            根据源文件hash创建模型上链信息文件(多个模型)
        """
        model_record_list = self.getModelRecordsByHash(source_file_hash)
        for model_record in model_record_list:
            self.createModelUpchainInfoFileSingle(source_file_hash,model_record.get("model_hash",""),model_info_config)

    def createModelUpchainInfoFileSingle(self,source_file_hash:str,model_hash:str,model_info_config:str)->bool:
        """
            创建模型上链信息文件
            param:
                - source_file_hash: 源文件hash
                - model_hash: 模型hash
                - model_info_config: 模型信息配置
            return:
                - bool: 是否成功
        """
        try:
            ml_client_path = self.tiny_db.get_ml_client_path()
            model_record = self.getModelRecordByHashAndHash(source_file_hash,model_hash)
            model_info = model_record.get("model_info", {})
            model_upchain_info = {
                "model_hash": model_hash,
                "model_name": model_info.get("model_name",""),
                "creator_user_id": "",
                "model_data_type": model_info.get("model_data_type",1), # 默认为流量数据
                "model_type": model_info.get("model_type",1),
                "model_algorithm": model_info.get("model_algorithm",""),
                "model_train_framework": model_info.get("model_framework",""),
                "model_open_source": model_info.get("open_source",1),
                "model_features": model_info.get("features",[]),
                "model_tags": model_info_config.get("tags",[]),
                "model_description": model_info_config.get("description",""),
                "model_size": model_info.get("model_size",0),
                "model_data_size": model_info.get("data_size",0),
                "model_data_ipfs_hash": "",
                "value": model_info_config.get("value",0),
                "model_ipfs_hash": "",
                "ref_cti_id": model_info.get("cti_id","")
            }
            # 保存到文件
            model_upchain_info_path = f"{ml_client_path}/model_records/{source_file_hash}/{model_hash}.json"
            os.makedirs(os.path.dirname(model_upchain_info_path), exist_ok=True)
            save_json_to_file(model_upchain_info_path, model_upchain_info)
            return True
        except Exception as e:
            logging.error(f"createModelUpchainInfoFile error:{e}")
            return False
            
    def saveModelUpchainResult(self,source_file_hash:str,model_hash:str,model_ipfs_hash:str,model_data_ipfs_hash:str)->bool:
        """
            保存模型上链结果
            param:
                - source_file_hash: 源文件hash
                - model_hash: 模型hash
                - model_ipfs_hash: 模型IPFS地址
                - model_data_ipfs_hash: 模型数据IPFS地址
            return:
                - bool: 是否成功
        """
        try:
            ml_client_path = self.tiny_db.get_ml_client_path()
            model_upchain_info_path = f"{ml_client_path}/model_records/{source_file_hash}/{model_hash}.json"
            if os.path.exists(model_upchain_info_path):
                model_upchain_info = load_json_from_file(model_upchain_info_path)
                model_upchain_info["model_ipfs_hash"] = model_ipfs_hash
                model_upchain_info["model_data_ipfs_hash"] = model_data_ipfs_hash
                save_json_to_file(model_upchain_info_path, model_upchain_info)
                return True
            return False
        except Exception as e:
            logging.error(f"saveModelUpchainResult error:{e}")
            return False

    def get_image_as_base64(self, image_path: str) -> str:
        """
        将图像文件转换为base64格式
        param:
            - image_path: 图像文件路径
        return:
            - str: base64编码的图像数据
        """
        try:
            if not os.path.exists(image_path):
                return None
            
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            logging.error(f"读取图像文件失败: {str(e)}")
            return None

    def get_model_image_path(self, request_id: str, image_type: str) -> str:
        """
        获取模型相关图像的路径
        params:
            - request_id: 请求ID
            - image_type: 图像类型(train_process/evaluation)
        return:
            - str: 图像路径
        """
        record = self.getModelRecordByRequestId(request_id)
        if not record:
            return None
        model_info = record.get('model_info',{})
        if image_type == 'train':
            train_results = model_info.get('train_results', {})
            return train_results.get('visualization_path')
        elif image_type == 'evaluation':
            eval_results = model_info.get('evaluation_results', {})
            return eval_results.get('visualization_path')
        return None

    def get_train_process_image_base64(self, request_id: str) -> str:
        """
        获取训练过程图像的base64编码
        """
        try:
            image_path = self.get_model_image_path(request_id, 'train')
            print(f"train_image_path: {image_path}")
            return self.get_image_as_base64(image_path)
        except Exception as e:
            logging.error(f"获取训练过程图像失败: {str(e)}")
            return None

    def get_model_evaluate_image_base64(self, request_id: str) -> str:
        """
        获取模型评估图像的base64编码
        """
        try:
            image_path = self.get_model_image_path(request_id, 'evaluation')
            print(f"evaluation_image_path: {image_path}")
            return self.get_image_as_base64(image_path)
        except Exception as e:
            logging.error(f"获取模型评估图像失败: {str(e)}")
            return None
