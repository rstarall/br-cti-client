from db.tiny_db import get_tiny_db_instance


# 负责调用大语言模型相关功能的服务层
class LlmService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()