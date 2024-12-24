from flask import Flask,jsonify,request
import logging
from flask import Blueprint  #导入蓝图模块
from blockchain.fabric import comment
comment_blue = Blueprint('comment',__name__,url_prefix='/comment') #创建一个蓝图

#注册评论
@comment_blue.route('/registerComment',methods=['POST'])
def registerComment():
    print("registerComment",request.json)
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    comment_data = request.json.get('comment_data')
    if not wallet_id or not password or not comment_data:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result,success = comment.registerComment(wallet_id, password, comment_data)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#审核评论
@comment_blue.route('/approveComment',methods=['POST'])
def approveComment():
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    comment_id = request.json.get('comment_id')
    if not wallet_id or not password or not comment_id:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result,success = comment.approveComment(wallet_id, password, comment_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#查询单个评论
@comment_blue.route('/queryComment',methods=['POST'])
def queryComment():
    comment_id = request.json.get('comment_id')
    if not comment_id:
        return jsonify({'code': 400, 'message': 'comment_id is required', 'data': None})
    result,success = comment.queryComment(comment_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})
    
#查询所有评论列表
@comment_blue.route('/queryAllCommentsByRefID',methods=['POST'])
def queryAllCommentsByRefID():
    ref_id = request.json.get('ref_id')
    if not ref_id:
        return jsonify({'code': 400, 'message': 'ref_id is required', 'data': None})
    result,success = comment.queryAllCommentsByRefID(ref_id)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})
   
#分页查询评论列表
@comment_blue.route('/queryCommentsByRefID',methods=['POST'])
def queryCommentsByRefID():
    ref_id = request.json.get('ref_id')
    page = request.json.get('page',1)
    page_size = request.json.get('page_size',10)
    if not ref_id:
        return jsonify({'code': 400, 'message': 'ref_id is required', 'data': None})
    result,success = comment.queryCommentsByRefID(ref_id, page, page_size)
    if success:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})

#创建评论交易
@comment_blue.route('/createCommentTransaction',methods=['POST'])
def createCommentTransaction():
    wallet_id = request.json.get('wallet_id')
    password = request.json.get('password')
    comment_data = request.json.get('comment_data')
    if not wallet_id or not password or not comment_data:
        return jsonify({'code': 400, 'message': '参数不完整', 'data': None})
    result = comment.createCommentTransaction(wallet_id, password, comment_data)
    if result:
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    else:
        return jsonify({'code': 400, 'message': result, 'data': None})
