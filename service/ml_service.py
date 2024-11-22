from db.tiny_db import get_tiny_db_instance
class MLService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
    def createTrainTask(self,task_id:str,task_type:str,task_data:dict)->bool:
        """
            创建训练任务
            return:True or False
        """
        return True
    def createTestTask(self,task_id:str,task_type:str,task_data:dict)->bool:
        """
            创建测试任务
            return:True or False
        """
        return True
