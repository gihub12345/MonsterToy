import os
from uuid import uuid4

import time
from bson import ObjectId

from flask import Blueprint, request, jsonify

from day9520190719.MonsterToy.baiduAI import text2audio, audio2text, my_nlp
from day9520190719.MonsterToy.redis_chat import set_redis
from day9520190719.MonsterToy.setting import db, RET, AUDIO_CHAT_PATH
from day9520190719.MonsterToy.utils import hint_speech

uploader_bp = Blueprint("uploader_bp", __name__)


# app应用向玩具发送语音消息
@uploader_bp.route("/app_uploader", methods=["POST"])
def app_uploader():
    # print(request.form.to_dict())
    # print(request.files)
    # 1.{'user_id': '5d3181a1aa47e8132727f8c4', 'to_user': '5d35a4f89b6f83911465ffcc'}
    # 2.定位 user_id 和 to_user 两个用所在的 Chat_window Chats表中查询数据
    # chat_window = MDB.Chats.find_one({"查询条件":"?"}) # 查询到聊天记录
    # 3.追加一条聊天记录 chat_window["chat_list"].append({聊天记录})
    # mdb.chats.update_one({},{"$push":{"chatlist":{聊天记录}}})
    """
    {
        "from_user" : user_id "5ca17c7aea512d26281bcb8d", // 信息发送方ID
        "to_user" : to_user "5ca17f85ea512d215cd9b079", // 信息接收方ID
        "chat" : request.files "c22b9edd-4e7a-4eee-94e7-b239a90b9b16.wav", // 语音消息文件名
        "createTime" :time.time() 1554376821.5634897 // 聊天创建时间
    }
    """

    # 4.问题来了 "chat" : request.files 要不要保存?
    # chat = {
    #     "from_user":request.form.user_id,
    #     "to_user":request.form.to_user,
    #     "chat":"文件名?",
    #     "createTime":time.time()
    # }
    # 5.如果保存,存在哪儿? 如果新建目录 要不要 增加 setting
    # 保存文件 在 Chat 目录
    # file_path = os.path.join("Chat","file_name")

    """
    {
        "code":0,
        "msg":"上传成功",
        "data":
        {
            "filename":"filename",
            "friend_type":"app"
        }
    }
    """
    # 6.返回值中需要一个 File_name 文件名是不是当前的这个聊天文件呢?
    #{"filename": "filename"} filename 是路径 还是 文件名呢?
    # 7.friend_type 这很明显是 当前用户的 类型 固定值app 因为当前是 app 上传的视图函数


    # 获取上传的字典信息
    chat_dict = request.form.to_dict()
    # 发送人id
    from_user = chat_dict.get("user_id")
    # 接收人id
    to_user = chat_dict.get("to_user")

    # 获取文件对象
    file_obj = request.files.get("reco_file")
    # 获取文件名
    filename = file_obj.filename
    # print(filename)
    # 文件路径
    file_path = os.path.join(AUDIO_CHAT_PATH, filename)
    # 保存文件
    file_obj.save(file_path)

    # 修改文件类型:amr类型转换成mp3类型
    os.system(f"ffmpeg -i {file_path} {file_path}.mp3")

    # 查询Chats数据库中的聊天记录
    # chat_id = db.Chats.find_one({"$and": [{"from_user": from_user}, {"to_user": to_user}]})
    chat_dict = db.Chats.find_one({"user_list": {"$all": [from_user, to_user]}})
    # print(chat_dict.get("_id"), ">>>>")

    # 聊天记录存在
    if chat_dict:
        # 聊天记录
        chat = {
            "from_user": from_user,
            "to_user": to_user,
            "chat": f"{filename}.mp3",
            "createTime": time.time(),
        }
        db.Chats.update({"_id": chat_dict.get("_id")}, {"$push": {"chat_list": chat}})

    # redis存储未读消息
    set_redis(to_user, from_user)

    # app应用发送给玩具的语音提示：
    """
    1.这个消息来自于谁，例如：你有来自{爸爸}的消息
    2.提示消息一般用 friend_remark
    3.TTS语音处理
    """
    # 语音消息提醒
    hint_info = hint_speech(to_user, from_user)

    # 返回参数
    RET["CODE"] = 0
    RET["MSG"] = "上传成功"
    RET["DATA"] = {
        "filename": hint_info,  # f"{filename}.mp3"
        "friend_type": "app"
    }

    return jsonify(RET)


# 玩具向app应用或者另一个玩具发送语音消息
@uploader_bp.route("/toy_uploader", methods=["POST"])
def toy_uploader():
    reco_file = request.files.get("reco")
    from_user = request.form.get("user_id")
    to_user = request.form.get("to_user")
    friend_type = request.form.get("friend_type")
    # print(from_user,to_user, friend_type,"22222222222")

    # 与app_uploader不同点：文件类型files.filename获取的是一个流式文件,需要手动添加wav文件后缀
    filename = f"{uuid4()}.wav"

    # 路径拼接，toy返回的wav文件保存位置
    file_path = os.path.join(AUDIO_CHAT_PATH, filename)
    # 文件保存
    reco_file.save(file_path)

    # 聊天的数据结构
    chat_info = {
        "from_user": from_user,
        "to_user": to_user,
        "chat": filename,
        "createTime": time.time()
    }
    # Chats数据表消息更新
    db.Chats.update({"user_list": {"$all": [from_user, to_user]}}, {"$push": {"chat_list": chat_info}})

    # 存储未读消息
    set_redis(to_user, from_user)

    # 玩具向其他玩具发送来的消息时，需要一个语音消息提醒，如果是app则不需要提醒，例如：你有来自{哥哥}的消息
    if friend_type == "toy":
        # 语音消息提醒
        filename = hint_speech(to_user, from_user)

    RET["CODE"] = 0
    RET["MSG"] = "上传成功"
    RET["DATA"] = {
        "filename": filename,
        "friend_type": "toy"
    }

    return jsonify(RET)


# 用于Toy录制语音消息上传至AI接口
@uploader_bp.route("/ai_uploader", methods=["POST"])
def ai_uploader():
    toy_id = request.form.get("toy_id")
    reco_file = request.files.get("reco")

    filename = f"{uuid4()}.wav"
    # 语音文件保存
    file_path = os.path.join(AUDIO_CHAT_PATH, filename)
    reco_file.save(file_path)

    # 语音识别
    text_speech = audio2text(file_path)
    print(text_speech, "........")
    # NLP自然语言处理
    res = my_nlp(text_speech, toy_id)

    return res




