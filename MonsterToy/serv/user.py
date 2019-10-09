from bson import ObjectId
from flask import Blueprint, request, jsonify

from day9520190719.MonsterToy.redis_chat import get_all_redis
from day9520190719.MonsterToy.setting import db, RET

user_bp = Blueprint("user_bp", __name__)


# 用户注册
@user_bp.route("/reg", methods=["POST"])
def reg():
    # 获取post请求的数据
    user_info = request.form.to_dict()

    # 新增数据结构
    user_info["avatar"] = "baba.jpg" if user_info.get("gender") == "2" else "mama.jpg"
    user_info["bind_toys"] = []
    user_info["friend_list"] = []

    # 存入数据库
    db.Users.insert_one(user_info)

    # 返回的数据类型
    RET["CODE"] = 0
    RET["MSG"] = "注册成功"
    RET["DATA"] = {}

    return jsonify(RET)


# 用户登录
@user_bp.route("/login", methods=["POST"])
def login():
    # 获取登录信息
    user_info = request.form.to_dict()
    # 数据库查询结果
    user_info_dict = db.Users.find_one(user_info)
    # 把ObjectId对象转换成str类型
    user_info_dict["_id"] = str(user_info_dict.get("_id"))

    RET["CODE"] = 0
    RET["MSG"] = f"用户{user_info_dict.get('nickname')}登录成功"
    RET["DATA"] = user_info_dict

    return jsonify(RET)


# 用户自动登录
@user_bp.route("/auto_login", methods=["POST"])
def auto_login():
    user_info = request.form.to_dict()
    # 把str数据类型转换成ObjectId类型
    user_info["_id"] = ObjectId(user_info.get("_id"))

    user_info_dict = db.Users.find_one(user_info)
    user_info_dict["_id"] = str(user_info_dict.get("_id"))

    # 通过当前用户ID查询当前登录用户的所有未读消息
    count_dict = get_all_redis(user_info_dict["_id"])
    #
    user_info_dict["chat"] = count_dict

    RET["CODE"] = 0
    RET["MSG"] = f"用户{user_info_dict.get('nickname')}登录成功"
    RET["DATA"] = user_info_dict

    return jsonify(RET)





