
import time
from tinydb import TinyDB, Query,where
from tinydb.storages import MemoryStorage
from concurrent.futures import ThreadPoolExecutor
import logging
from utils.file import get_project_root_path
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
        #初始化数据库
        self.local_db_map = {
            "default":get_project_root_path()+"/db/db.json",
            "stix_records":data_client_path+"/stix_records.json",
            "cti_records":data_client_path+"/cti_records.json",
            "stix_process_progress":data_client_path+"/stix_process_progress.json",
            "cti_process_progress":data_client_path+"/cti_process_progress.json",
            "ml_records":ml_client_path+"/ml_records.json",
        }
        self.db_path = self.local_db_map["default"]
        data = {"app": "br-cti-client", "version": '1.0'}
        self.upsert_by_key_value( "config", data,"version",'1.0')
        logging.info("init tinydb success.")
        logging.info(f"db path:{self.db_path}")
    def use_database(self,db_name):
        """
            使用指定的数据库
            param:
                db_name: 数据库名(default,stix_records,cti_records,ml_records)
            return:
                self
        """
        self.db_path = self.local_db_map.get(db_name,self.local_db_map["default"])
        return self
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
        #为数据增加或更新时间戳
        data['timestamp']=int(round(time.time() * 1000))
        db = TinyDB(self.db_path)
        table = db.table(table_name)
        query = Query()
        doc_ids = [doc.doc_id for doc in table.search(query[fieldName] == value)]
        # 如果找到了匹配的文档，则更新
        if doc_ids:
            table.update(data, doc_ids=doc_ids)
            logging.info(f"Updated existing document(s) with {fieldName}={value}.")
        else:
            # 如果没有找到匹配的文档，则插入新数据
            table.insert(data)
            logging.info(f"Inserted new document with {fieldName}={value} as no existing match was found.")
        db.close()

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
        db = TinyDB(self.db_path)
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
        db.close()
    def write(self, table_name, data = None):
        db = TinyDB(self.db_path)
        table = db.table(table_name)
        if data != None:
            table.insert(data)
        db.close()
    def clear_table(self, table_name):
        db = TinyDB(self.db_path)
        table = db.table(table_name)
        # 清空表中的数据
        table.truncate()
        db.close()
        
    def timely_write(self, table_name, data):
        
        #为数据增加时间戳(精确到ms)
        data['timestamp']=int(round(time.time() * 1000))
        return self.write(table_name, data)
    def read(self, table_name, query=None):

        db = TinyDB(self.db_path)
        table = db.table(table_name)
        if query:
            result = table.search(query)
        else:
            result = table.all()
        db.close()
        return result
    
    def read_sort_by_timestamp(self, table_name, limit = 0,order_by_time = False,  field_name=None, field_value = None):
      
        db = TinyDB(self.db_path)
        table = db.table(table_name)
        
        if field_name:
            # 构造查询，例如查询字段名为'field_name'且值为'value'
            query = where(field_name) == field_value  # 注意：这里'value'需要替换成实际值或从参数中获取
            results = table.search(query)
        else:
            results = table.all()
        
        # 如果需要按时间排序，这里假设每个文档都有一个名为'timestamp'的时间戳字段
        if order_by_time:
            results.sort(key=lambda x: x['timestamp'])  # 假设时间戳字段名为'timestamp'
            # 如果需要降序，可以改为: results.sort(key=lambda x: x['timestamp'], reverse=True)           
        db.close()
        #返回指定数量的结果
        if limit > 0:
            results = results[:limit]
        
        return results
    
    def read_by_key_value(self, table_name,field_name=None, field_value = None):
        db = TinyDB(self.db_path)
        table = db.table(table_name)
        results=[]
        if field_name:
            # 构造查询，例如查询字段名为'field_name'且值为'value'
            query = where(field_name) == field_value  # 注意：这里'value'需要替换成实际值或从参数中获取
            results = table.search(query)  
        if len(results)>0:
            return results
        return None
       
