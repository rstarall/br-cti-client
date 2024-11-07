from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from utils.request import POST
ml_blue = Blueprint('ml',__name__,url_prefix='/ml') #创建一个蓝图