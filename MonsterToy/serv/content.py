import os
from flask import Blueprint, request, jsonify, send_file
from day9520190719.MonsterToy.setting import COVERT_PATH, MUSIC_PATH, QRCODE_PATH, RET, AUDIO_CHAT_PATH

from day9520190719.MonsterToy.setting import db

content_bp = Blueprint("content_bp", __name__)


# 音乐信息
@content_bp.route("/content_list", methods=["POST"])
def content_list():
    # 获取数据库中的所有音乐信息
    content = db.Content.find({})
    print(content)
    # 把Cursor对象转换成list类型
    content = list(content)

    # 把ObjectId对象转换成字符串
    for index, item in enumerate(content):
        content[index]["_id"] = str(item.get("_id"))

    # 返会json对象
    return jsonify(content)


# 获取音乐资源
@content_bp.route("/get_music/<filename>")
def get_music(filename):
    # 音乐文件路径
    music_path = os.path.join(MUSIC_PATH, filename)

    return send_file(music_path)


# 获取图片资源
@content_bp.route("/get_cover/<filename>")
def get_cover(filename):
    # 封面文件路径
    cover_path = os.path.join(COVERT_PATH, filename)

    return send_file(cover_path)


# 获取玩具二维码电子版
@content_bp.route("/get_qr/<qrname>")
def get_qr(qrname):
    # 设备二维码存放路径
    qrfile_path = os.path.join(QRCODE_PATH, qrname)

    # 发送二维码文件
    return send_file(qrfile_path)


# 获取玩具语音消息,语音格式：mp3
@content_bp.route("/get_chat/<chatname>")
def get_chat(chatname):
    file_path = os.path.join(AUDIO_CHAT_PATH, chatname)

    # 发送本地文件夹中的语音消息
    return send_file(file_path)

