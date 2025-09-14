from flask import Flask, jsonify, request, Blueprint
import logging
import uuid
from datetime import datetime
from service.rag_service import RAGService
from utils.request import request_post, request_get

# 创建RAG蓝图
rag_blue = Blueprint('rag', __name__, url_prefix='/rag')
rag_service = RAGService()

def get_user_context(request):
    """获取用户上下文信息"""
    # 这里可以从请求中获取用户信息、当前查看的威胁情报等
    return {
        "user_id": request.headers.get("X-User-Id", "anonymous"),
        "current_view": request.args.get("current_view", ""),
        "client_ip": request.remote_addr
    }

@rag_blue.route('/chat', methods=['POST'])
def chat():
    """
    RAG聊天接口 - 与威胁情报系统集成
    """
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        use_stream = data.get('use_stream', False)
        
        if not message:
            return jsonify({
                "code": 400,
                "msg": "消息不能为空",
                "data": None
            }), 400
        
        # 获取CTI系统上下文
        cti_context = {
            "system": "br-cti-client",
            "user_context": get_user_context(request),
            "use_web": data.get('use_web', False),
            "use_graph": data.get('use_graph', True),
            "timestamp": datetime.now().isoformat()
        }
        
        # 调用RAG服务
        result = rag_service.chat(message, session_id, cti_context, use_stream)
        
        if result["status"] == "success":
            return jsonify({
                "code": 200,
                "msg": "success",
                "data": result["data"]
            })
        else:
            return jsonify({
                "code": 500,
                "msg": result["message"],
                "data": None
            }), 500
            
    except Exception as e:
        logging.error(f"RAG聊天接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": str(e),
            "data": None
        }), 500

@rag_blue.route('/knowledge/add', methods=['POST'])
def add_knowledge():
    """
    添加威胁情报知识到RAG系统
    """
    try:
        data = request.get_json()
        content = data.get('content')
        metadata = data.get('metadata', {})
        
        result = rag_service.add_knowledge(content, metadata)
        
        if result["status"] == "success":
            return jsonify({
                "code": 200,
                "msg": "威胁情报知识添加成功",
                "data": result["data"]
            })
        else:
            return jsonify({
                "code": 500,
                "msg": result["message"],
                "data": None
            }), 500
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e),
            "data": None
        }), 500

@rag_blue.route('/sessions/<session_id>/history', methods=['GET'])
def get_chat_history(session_id):
    """
    获取聊天历史
    """
    try:
        result = rag_service.get_chat_history(session_id)
        
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": result["data"] if result["status"] == "success" else None
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e),
            "data": None
        }), 500

@rag_blue.route('/sessions', methods=['POST'])
def create_session():
    """
    创建新的聊天会话
    """
    try:
        session_id = str(uuid.uuid4())
        
        return jsonify({
            "code": 200,
            "msg": "会话创建成功",
            "data": {"session_id": session_id}
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e),
            "data": None
        }), 500

@rag_blue.route('/health', methods=['GET'])
def health_check():
    """
    RAG系统健康检查
    """
    try:
        # 检查RAG系统状态
        status = {
            "rag_system": "running",
            "milvus": "checking...",
            "neo4j": "checking...",
            "redis": "checking..."
        }
        
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": status
        })
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str(e),
            "data": None
        }), 500
