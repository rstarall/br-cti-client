#启动Flask服务器
import logging
from flask import Flask
from server.handler.bc_handler import bc_blue
from server.handler.data_handler import data_blue
from server.handler.ml_handler import ml_blue
from server.handler.user_handler import user_blue
logging.basicConfig(level=logging.INFO)#保留error及以上级别的日志
app = Flask(__name__)
"""
    注册控制器蓝图
"""
app.register_blueprint(bc_blue) #区块链API
app.register_blueprint(data_blue) #数据处理API
app.register_blueprint(ml_blue)  #模型API
app.register_blueprint(user_blue) #用户API

