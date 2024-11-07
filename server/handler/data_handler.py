from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from utils.request import POST
data_blue = Blueprint('data',__name__,url_prefix='/data') #创建一个蓝图