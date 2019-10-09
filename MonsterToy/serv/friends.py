import time

from bson import ObjectId
from flask import Blueprint, request, jsonify

from day9520190719.MonsterToy.baiduAI import text2audio
from day9520190719.MonsterToy.redis_chat import get_redis, get_redis_toy
from day9520190719.MonsterToy.setting import db, RET
from day9520190719.MonsterToy.utils import hint_speech

friend_bp = Blueprint("friend_bp", __name__)


# 好友列表
@friend_bp.route("/friend_list", methods=["POST"])
def friend_list():
    user_id = request.form.get("_id")
    user_info = db.Users.find_one({"_id": ObjectId(user_id)})

    RET["CODE"] = 0
    RET["MSG"] = "好友查询"
    RET["DATA"] = user_info.get("friend_list")
    # print(user_info)
    return jsonify(RET)


# 聊天列表
@friend_bp.route("/chat_list", methods=["POST"])
def chat_list():
    chat = request.form.to_dict()

    # 查询聊天列表
    chat_window = db.Chats.find_one({"_id": ObjectId(chat.get("chat_id"))})

    # 获取未读消息数
    get_redis(chat.get("to_user"), chat.get("from_user"))

    RET["CODE"] = 0
    RET["MSG"] = "查询聊天记录"
    RET["DATA"] = chat_window.get("chat_list")

    return jsonify(RET)


# 通过玩具手动接收用户传来的信息
@friend_bp.route("/recv_msg", methods=["POST"])
def recv_msg():
    chat_info = request.form.to_dict()

    # 从redis中读取未读消息条数
    count, from_user = get_redis_toy(chat_info.get("to_user"), chat_info.get("from_user"))
    # 蜜汁逻辑 count == 0 代表当前 from_user 没有未读消息了
    # 要不要 读取 有未读消息的用户呢?

    # 这是from_user则是其他的好友的未读信息
    user_list = [from_user, chat_info.get("to_user")]
    chat_window = db.Chats.find_one({"user_list": {"$all": user_list}})

    # 读取Chats中chat_list里面的最后一条数据
    # chat_info_list = chat_window.get("chat_list")[-1:]  # type:list

    # 通过redis中查询未读消息条数，读取相应Chats中的消息条数
    if not count:
        # 当前未读消息为0
        pass
    else:
        # 消息列表
        chat_info_list = chat_window.get("chat_list")[-count:]  # type:list

        # 在这里增加一个语音提示 , "以下是来自 XX 的N条消息"
        # 查询Toys表，获取字典数据
        # toy_dict = db.Toys.find_one({"_id": ObjectId(chat_info.get("to_user"))})
        # for friend in toy_dict.get("friend_list"):
        #     # 获取当前发送消息者的尊称
        #     friend_remark = friend.get("friend_remark")
        #     # 自定义消息字符串
        #     text_content = f"这是来自{friend_remark}的未读消息"
        #     # TTS，语音合成，格式MP3
        #     filename = text2audio(text_content)
        # 语音提示
        filename, friend_type = hint_speech(chat_info.get("to_user"), from_user, info_type="xx")

        # 创建Chats的消息数据结构
        chat_dict = {
            "from_user": chat_info.get("from_user"),
            "to_user": chat_info.get("to_user"),
            "chat": filename,
            "createTime": time.time()
        }

        # chat_info_list.append(chat_dict)
        chat_info_list.insert((len(chat_info_list)-2*count), chat_dict)

        # 反转消息列表，使听取消息的时候听取到最先接受到的消息
        chat_info_list.reverse()

        # 返回前端的字典数据
        ret = {
            "from_user": from_user,
            "friend_type": friend_type,
            "chat_list": chat_info_list
        }

        return jsonify(ret)


# 添加好友
@friend_bp.route("/add_req", methods=["POST"])
def add_req():
    req_dict = request.form.to_dict()

    # 判断请求对象 toy or app
    add_user_type = req_dict.get("add_type")
    # 请求是玩具toy
    if add_user_type == "toy":
        # 玩具信息
        toy_dict = db.Toys.find_one({"_id": ObjectId(req_dict.get("add_user"))})
        req_dict["avatar"] = toy_dict.get("avatar")
        req_dict["nickname"] = toy_dict.get("baby_name")
    else:
        # 用户信息
        user_dict = db.Users.find_one({"_id": ObjectId(req_dict.get("add_user"))})
        req_dict["avatar"] = user_dict.get("avatar")
        req_dict["nickname"] = user_dict.get("nickname")

    # 好友请求状态 1同意 0未处理 2拒绝
    req_dict["status"] = 0
    # 接收放一定是玩具对象
    toy_dict_rec = db.Toys.find_one({"_id": ObjectId(req_dict.get("toy_id"))})
    req_dict["toy_name"] = toy_dict_rec.get("baby_name")

    # 把数据写入Request数据表
    db.Request.insert_one(req_dict)

    RET["CODE"] = 0
    RET["MSG"] = "添加好友请求成功"
    RET["DATA"] = {}

    return jsonify(RET)


# 好友请求列表
@friend_bp.route("/req_list", methods=["POST"])
def req_list():
    user_id = request.form.get("user_id")

    # 通过user_id获取用户数据字典
    user_dict = db.Users.find_one({"_id": ObjectId(user_id)})
    # 用户绑定的所有bind_toys
    bind_toys = user_dict.get("bind_toys")

    # 查询Request数据表中玩具id，和状态 0 的数据
    add_req_list = list(db.Request.find({"toy_id": {"$in": bind_toys}, "status": 0}))

    # ObjectId转换成str
    for item in add_req_list:
        item["_id"] = str(item.get("_id"))

    RET["CODE"] = 0
    RET["MSG"] = "查询好友请求"
    RET["DATA"] = add_req_list

    return jsonify(RET)


# 好友请求处理(同意添加好友)
@friend_bp.route("/acc_req", methods=["POST"])
def acc_req():
    req = request.form.to_dict()
    print(req, "1122222")
    req_id = req.get("req_id")
    remark = req.get("remark")

    # 查询request数据表中的字典数据
    request_dict = db.Request.find_one({"_id": ObjectId(req_id)})
    print(request_dict.get("remark"), "3333")
    """
        "_id" : ObjectId("5d394fe1b120b9980de90134"),
        "add_user" : "5d3948c9b558516940ad5eac",
        "toy_id" : "5d394881b558516940ad5eaa",
        "add_type" : "toy",
        "req_info" : "变形金刚",
        "remark" : "弟弟",
        "avatar" : "toy.jpg",
        "nickname" : "圆圆",
        "status" : 0,
        "toy_name" : "天天"
    """
    # 请求方ID
    add_user = request_dict.get("add_user")
    # 被请求方ID
    toy_id = request_dict.get("toy_id")

    # 添加好友后需要创建Chats聊天数据
    chat_id = db.Chats.insert_one({"user_list": [add_user, toy_id], "chat_list": []})

    # 添加好友名片
    """
        "friend_id" : "5d39482eb558516940ad5ea8",
        "friend_nick" : "sss",
        "friend_remark" : "爸爸",
        "friend_avatar" : "toy.jpg",
        "friend_chat" : "5d3948c9b558516940ad5eab",
        "friend_type" : "app"
    """
    # 1. 被请求方(toy)添加好友名片(toy or app)
    # 判断添加好友的类型：玩具 or 用户
    if request_dict.get("add_type") == "toy":
        user_dict = db.Toys.find_one({"_id": ObjectId(add_user)})
    else:
        user_dict = db.Users.find_one({"_id": ObjectId(add_user)})

    # 被请求方添加好友数据结构
    toy_add_user = {
        "friend_id": add_user,
        "friend_nick": user_dict.get("baby_name") if user_dict.get("baby_name") else user_dict.get("nickname"),
        "friend_remark": remark,
        "friend_avatar": user_dict.get("avatar"),
        "friend_chat": str(chat_id.inserted_id),
        "friend_type": request_dict.get("add_type")
    }

    # 2. 请求方(toy or app)添加被请求方(toy)的好友名片
    # 请求方添加好友数据结构
    user_add_toy = {
        "friend_id": toy_id,
        "friend_nick": request_dict.get("toy_name"),
        "friend_remark": request_dict.get("remark"),
        "friend_avatar": request_dict.get("avatar"),
        "friend_chat": str(chat_id.inserted_id),
        "friend_type": "toy"
    }

    # 被请求方添加好友的数据表更新
    if request_dict.get("add_type") == "toy":
        db.Toys.update_one({"_id": ObjectId(add_user)}, {"$push": {"friend_list": user_add_toy}})
    else:
        db.Users.update_one({"_id": ObjectId(add_user)}, {"$push": {"friend_list": user_add_toy}})

    # 请求方添加好友的数据表更新
    db.Toys.update_one({"_id": ObjectId(toy_id)}, {"$push": {"friend_list": toy_add_user}})

    # 更新好友请求Request表中status状态更新
    db.Request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})

    RET["CODE"] = 0
    RET["MSG"] = "同意添加好友"
    RET["DATA"] = {}

    return jsonify(RET)


# 好友请求处理(拒绝添加好友)
@friend_bp.route("/ref_req", methods=["POST"])
def ref_req():
    req_id = request.form.get("req_id")

    # 更新好友请求状态 1同意 0未处理 2拒绝
    db.Request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 2}})

    RET["CODE"] = 0
    RET["MSG"] = "拒绝添加好友"
    RET["DATA"] = {}

    return jsonify(RET)





