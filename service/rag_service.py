from db.tiny_db import get_tiny_db_instance
from datetime import datetime
import logging
import asyncio
import uuid
from threatRAG.integration.rag_wrapper import threat_rag

class RAGService:
    """RAG服务层，处理与CTI系统的集成逻辑"""
    
    def __init__(self):
        self.tiny_db = get_tiny_db_instance()
    
    def chat(self, message: str, session_id: str = None, user_context: dict = None, use_stream: bool = False):
        """
        处理聊天请求
        """
        try:
            # 如果没有session_id，创建新的
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 添加CTI系统特定的上下文
            enhanced_context = self._enhance_context(user_context)
            
            # 调用RAG能力（同步调用异步方法）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    threat_rag.chat(message, session_id, enhanced_context, use_stream)
                )
            finally:
                loop.close()
            
            # 保存聊天记录到数据库
            if result["status"] == "success":
                self.save_chat_record(session_id, message, result)
            
            return result
            
        except Exception as e:
            logging.error(f"RAG服务聊天失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def add_knowledge(self, content: str, metadata: dict = None):
        """
        添加知识，可能来自威胁情报数据
        """
        # 增强元数据，添加CTI系统特有信息
        enhanced_metadata = self._enhance_metadata(metadata)
        
        return threat_rag.add_knowledge(content, enhanced_metadata)
    
    def get_chat_history(self, session_id: str):
        """
        获取聊天历史
        """
        return threat_rag.get_chat_history(session_id)
    
    def save_chat_record(self, session_id: str, message: str, rag_result: dict):
        """
        保存聊天记录到CTI系统数据库
        """
        try:
            record = {
                "session_id": session_id,
                "user_message": message,
                "ai_response": rag_result.get("data", {}).get("response", ""),
                "sources": rag_result.get("data", {}).get("sources", []),
                "status": rag_result.get("status", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "metadata": rag_result.get("data", {}).get("metadata", {})
            }
            
            self.tiny_db.insert("rag_chat_history", record)
            logging.info(f"RAG聊天记录已保存: {session_id}")
            
        except Exception as e:
            logging.error(f"保存RAG聊天记录失败: {e}")
    
    def _enhance_context(self, user_context: dict) -> dict:
        """
        增强上下文，添加CTI系统特有信息
        """
        enhanced = user_context or {}
        
        # 可以添加当前用户正在查看的威胁情报
        # 添加用户权限信息
        # 添加系统状态信息等
        
        enhanced.update({
            "system": "br-cti-client",
            "timestamp": datetime.now().isoformat(),
            # 可以从区块链或其他服务获取更多上下文
        })
        
        return enhanced
    
    def _enhance_metadata(self, metadata: dict) -> dict:
        """
        增强元数据，添加CTI系统特有信息
        """
        enhanced = metadata or {}
        
        enhanced.update({
            "source_system": "br-cti-client",
            "added_at": datetime.now().isoformat(),
            "content_type": "threat_intelligence"
        })
        
        return enhanced
