#启动Flask服务器
import logging
from flask import Flask
from flask_cors import CORS
from server.handler.index_handler import index_blue
from server.handler.bc_handler import bc_blue
from server.handler.data_handler import data_blue
from server.handler.ml_handler import ml_blue
from server.handler.user_handler import user_blue
logging.basicConfig(level=logging.INFO)#保留error及以上级别的日志
app = Flask(__name__)
# 允许所有来源的请求(本地请求会产生跨域)
# 需要安装跨域扩展
CORS(app)
"""
    注册控制器蓝图
"""
app.register_blueprint(index_blue)#根路由
app.register_blueprint(bc_blue) #区块链API
app.register_blueprint(data_blue) #数据处理API
app.register_blueprint(ml_blue)  #模型API
app.register_blueprint(user_blue) #用户API

#一些配置(文件上传大小约束)
app.config['MAX_CONTENT_LENGTH'] = 100*1024 * 1024 * 1024  # 100GB limit

