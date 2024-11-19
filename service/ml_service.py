from db.tiny_db import get_tiny_db_instance
class MLService:
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()