from bson import ObjectId

from day9520190719.MonsterToy.baiduAI import text2audio, db


def hint_speech(to_user, from_user, info_type=None):
    # 发送消息的用户不存在
    friend_remark = "未知用户"
    # 好友类型：toy or app
    friend_type = None
    # 查询接收人信息
    toy_info = db.Toys.find_one({"_id": ObjectId(to_user)})
    # Toys的好友列表
    toy_friend_list = toy_info.get("friend_list")
    for friend in toy_friend_list:
        # 判断是否是好友发送来的消息
        if friend.get("friend_id") == from_user:
            # 获取好友昵称
            friend_remark = friend.get("friend_remark")
            # 获取好友类型
            friend_type = friend.get("friend_type")
        else:
            # 好友信息不匹配
            friend_type = None

    if not info_type:
        # TTS语音合成
        hint_info = text2audio(f"你有来自{friend_remark}的消息")
        return hint_info
    else:
        hint_info = text2audio(f"以下是来自{friend_remark}的消息")
        return hint_info, friend_type




