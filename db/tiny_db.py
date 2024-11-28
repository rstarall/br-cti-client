import time
from tinydb import TinyDB, Query,where
from utils.file import get_project_root_path
import logging
import os

logging.basicConfig(level=logging.INFO)
db_instance = None
def get_tiny_db_instance():
    """
        获取tinydb实例
    """
    global db_instance
    if db_instance is None:
        db_instance = TinyDBUtil()
    return db_instance

class TinyDBUtil:
    def __init__(self):
        data_client_path = get_project_root_path()+"/db/data_client"
        ml_client_path = get_project_root_path()+"/db/ml_client"
        progress_path = get_project_root_path()+"/db/progress"
        #初始化数据库
        self.local_db_map = {
            "default":get_project_root_path()+"/db/db.json",
            "stix_records":data_client_path+"/stix_records/stix_records.json",
            "cti_records":data_client_path+"/cti_records/cti_records.json",
            "ml_records":ml_client_path+"/ml_records.json",
            "stix_process_progress":progress_path+"/stix_process_progress.json",
            "cti_process_progress":progress_path+"/cti_process_progress.json",
            "cti_upchain_progress":progress_path+"/cti_upchain_progress.json",
            "ml_process_progress":progress_path+"/ml_process_progress.json",
        }
        self.db_name = "default"
        self.db_path = self.local_db_map["default"]
        self.db_instance_map = {
            "default":TinyDB(self.db_path)
        }
        data = {"app": "br-cti-client", "version": '1.0'}
        self.upsert_by_key_value( "config", data,"version",'1.0')
        logging.info("init tinydb success.")
        logging.info(f"db path:{self.db_path}")

    def get_data_client_path(self):
        """
            获取data client数据库路径
        """
        return get_project_root_path()+"/db/data_client"
    
    def get_ml_client_path(self):
        """
            获取ml client数据库路径
        """
        return get_project_root_path()+"/db/ml_client"
    def use_database(self,db_name):
        """
            使用指定的数据库
            param:
                db_name: 数据库名(default,stix_records,cti_records,ml_records)
            return:
                self
        """
        self.db_name = db_name
        self.db_path = self.local_db_map.get(db_name,self.local_db_map["default"])
        #创建数据库实例
        self.get_db_instance(db_name)
        return self
    
    def open_table(self,table_name):
        """
            打开指定的表
            param:
                table_name: 表名
            return:
                table: 表
        """
        db = self.get_db_instance()
        return db.table(table_name)
    
    def get_db_instance(self,db_name=None):
        """
            获取数据库实例
        """
        if db_name is None:
            if self.db_name is None:
                raise Exception("db_name is None")
            db_name = self.db_name

        db = self.db_instance_map.get(db_name,None)
        if db is None:
            if not os.path.exists(self.db_path):
                db_dir_path = os.path.dirname(self.db_path)
                if not os.path.exists(db_dir_path):
                    os.makedirs(db_dir_path)
                with open(self.db_path, 'w') as f:
                    f.write('{}')
            db = TinyDB(self.db_path)
            self.db_instance_map[self.db_name] = db
        return db


    def upsert_by_key_value(self, table_name, data, fieldName, value):
        """
            根据key==value寻找主行，然后更新或插入数据
            param:
                table_name: 表名
                data: 数据
                fieldName: 字段名
                value: 字段值
            return:
                None
        """
        db = self.get_db_instance()
        table = db.table(table_name)
        query = Query()
        doc_ids = [doc.doc_id for doc in table.search(query[fieldName] == value)]

        #为数据增加或更新时间戳
        data['timestamp'] = int(round(time.time() * 1000))
        
        # 如果找到了匹配的文档，则更新
        if doc_ids:
            table.update(data, doc_ids=doc_ids)
            logging.info(f"Updated existing document(s) with {fieldName}={value}.")
        else:
            # 如果没有找到匹配的文档，则插入新数据
            table.insert(data)
            logging.info(f"Inserted new document with {fieldName}={value} as no existing match was found.")
        
        # 移除这里的 db.close()，让数据库连接保持开启状态

    def update_single_value(self, table_name, fieldName, value, update_key, update_value):
        """
            根据fieldName==value寻找主行，然后更新数据的单个字段
            param:
                table_name: 表名
                fieldName: 字段名
                value: 字段值
                update_key: 更新字段名
                update_value: 更新字段值
        """
        db = self.get_db_instance()
        table = db.table(table_name)
        query = Query()
        docs= [doc for doc in table.search(query[fieldName] == value)]
        # 如果找到了匹配的文档，则更新
        if docs:
            for doc in docs:
                doc[update_key] = update_value
                table.update(doc, doc_ids=doc.doc_id)
            logging.info(f"Updated existing document(s) with {fieldName}={value}.")
        else:
            # 如果没有找到匹配的文档，则插入新数据
            logging.info(f"no found document with {fieldName}={value}.")

    def write(self, table_name, data = None):
        db = self.get_db_instance()
        table = db.table(table_name)
        if data != None:
            table.insert(data)

    def clear_table(self, table_name):
        db = self.get_db_instance()
        table = db.table(table_name)
        # 清空表中的数据
        table.truncate()
        
    def timely_write(self, table_name, data):
        #为数据增加时间戳(精确到ms)
        data['timestamp']=int(round(time.time() * 1000))
        return self.write(table_name, data)
    
    def read(self, table_name, query=None):
        db = self.get_db_instance()
        table = db.table(table_name)
        if query:
            result = table.search(query)
        else:
            result = table.all()
        return result
    
    def read_sort_by_timestamp(self, table_name, limit = 0, order_by_time = False, field_name=None, field_value = None):
        db = self.get_db_instance()
        table = db.table(table_name)
        
        if field_name:
            query = where(field_name) == field_value
            results = table.search(query)
        else:
            results = table.all()
        
        # 如果需要按时间排序
        if order_by_time:
            results.sort(key=lambda x: x['timestamp'])
        
        # 返回指定数量的结果
        if limit > 0:
            results = results[:limit]
        
        return results
    
    def read_by_key_value(self, table_name,field_name=None, field_value = None):
        db = self.get_db_instance()
        table = db.table(table_name)
        results=[]
        if field_name:
            # 构造查询，例如查询字段名为'field_name'且值为'value'
            query = where(field_name) == field_value  # 注意：这里'value'需要替换成实际值或从参数中获取
            results = table.search(query)  
        if len(results)>0:
            return results
        return None
       
