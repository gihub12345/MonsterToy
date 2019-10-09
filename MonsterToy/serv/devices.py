import time

from bson import ObjectId
from flask import Blueprint, request, jsonify
from day9520190719.MonsterToy.setting import RET,db

devices_bp = Blueprint("devices_bp", __name__)


# 识别二维码信息
@devices_bp.route("/scan_qr", methods=["POST"])
def scan_qr():
    # 获取到device_key
    device_key = request.form.to_dict()
    # 查看Toys设备是否绑定
    # device_dict = db.Toys.find_one({"device_key": ??})
    toy_dict = db.Toys.find_one(device_key)

    # 设备未绑定状态
    if not toy_dict:
        # 查询是否存在此设备
        devices_info = db.Devices.find_one(device_key)
        if devices_info:
            # 二维码扫描成功
            RET["CODE"] = 0
            RET["MSG"] = "二维码扫描成功"
            RET["DATA"] = device_key
        else:
            # 二维码扫描失败
            RET["CODE"] = 1
            RET["MSG"] = "扫描二维码失败"
            RET["DATA"] = device_key
    else:
        # 二维码扫描成功, 但设备已经进行绑定
        RET["CODE"] = 2
        RET["MSG"] = "设备已经进行绑定"
        RET["DATA"] = {"toy_id": str(toy_dict.get("_id"))}

    return jsonify(RET)


# 绑定toy设备
@devices_bp.route("/bind_toy", methods=["POST"])
def bind_toy():
    # 获取toy信息
    toy_info = request.form.to_dict()

    # 增加字段
    toy_info["avatar"] = "toy.jpg"
    user_id = toy_info.pop("user_id")  # 删除字段，获取到字段的值
    toy_info["bind_user"] = user_id
    toy_info["friend_list"] = []

    # app与toy的聊天记录数据结构
    chat = {
        "user_list": [],
        "chat_list": []
    }
    # 添加数据结构到数据库，生成ObjectId
    chat_info = db.Chats.insert_one(chat)

    # 根据用户获取到用户信息
    user_info = db.Users.find_one({"_id": ObjectId(user_id)})
    # toy添加app的名片信息
    t_add_a = {
        "friend_id": user_id,
        "friend_nick": user_info.get("nickname"),
        "friend_remark": toy_info.get("remark"),
        "friend_avatar": "toy.jpg",
        "friend_chat": str(chat_info.inserted_id),
        "friend_type": "app"
    }

    # toy添加app的名片信息
    toy_info["friend_list"].append(t_add_a)
    # 创建Toys的数据库表，并添加信息
    toy_id = db.Toys.insert_one(toy_info)

    # app添加toy的名片信息
    a_add_t = {
        "friend_id": str(toy_id.inserted_id),
        "friend_nick": toy_info.get("baby_name"),
        "friend_remark": toy_info.get("toy_name"),
        "friend_avatar": "toy.jpg",
        "friend_chat": str(chat_info.inserted_id),
        "friend_type": "toy"
    }

    # 添加设备的id信息 bind_toys
    user_info["bind_toys"].append(str(toy_id.inserted_id))
    # app添加toy的名片信息
    user_info["friend_list"].append(a_add_t)
    # 更新Users数据库
    db.Users.update_one({"_id": user_info.get("_id")}, {"$set": user_info})

    # app与toy的聊天记录数据结构的完善
    """
    chat = {
        "user_list": [],
        "chat_list": []
    }
    """
    chat_info_dict = {
        "from_user": toy_info.get("device_key"),
        "to_user": user_id,
        "chat": "",
        "createTime": time.time()
    }
    # 添加完善的数据结构
    chat["user_list"] = [user_id, str(toy_id.inserted_id)]
    chat["chat_list"].append(chat_info_dict)
    # 更新Chats数据库
    db.Chats.update({"_id": ObjectId(chat_info.inserted_id)}, {"$set": chat})

    # 返回值信息
    RET["CODE"] = 0
    RET["MSG"] = "绑定完成"
    RET["DATA"] = {}

    return jsonify(RET)


# 设备toy列表
@devices_bp.route("/toy_list", methods=["POST"])
def toy_list():
    user_id = request.form.get("_id")

    # 通过用户id查询所有的绑定的设备
    toys = list(db.Toys.find({"bind_user": user_id}))

    for toy in toys:
        toy["_id"] = str(toy.get("_id"))

    RET["CODE"] = 0
    RET["MSG"] = "获取Toy列表"
    RET["DATA"] = toys

    return jsonify(RET)


# 打开链接设备
@devices_bp.route("/open_toy", methods=["POST"])
def open_toy():
    device_key = request.form.to_dict()
    # 1.用 device_key 查询? Devices or Toys
    # 先查询已绑定Toy 可以有效减少数据库查询次数(减少IO操作)
    toy = db.Toys.find_one(device_key)
    # 2.设备处于绑定状态,正常启动
    # 设备未绑定
    # 设备未授权 0.5%
    if toy:  # 开机成功
        ret = {
            "code": 0,
            "music": "Success.mp3",
            "toy_id": str(toy.get("_id")),
            "name": toy.get("toy_name")
        }
    else:
        # 设备未绑定
        if db.Devices.find_one(device_key):
            ret = {
                "code": 1,
                "music": "Nobind.mp3"
            }
        # 设备未授权
        else:
            ret = {
                "code": 2,
                "music": "Nolic.mp3"
            }

    return jsonify(ret)





