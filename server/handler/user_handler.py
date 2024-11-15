
from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
user_blue = Blueprint('user',__name__,url_prefix='/user') #创建一个蓝图
