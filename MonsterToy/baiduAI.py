import os
from bson import ObjectId

from day9520190719.MonsterToy.my_nlp11 import my_nlp_content
from day9520190719.MonsterToy.setting import SPEECH_CLIENT, VIOCE, AUDIO_CHAT_PATH, db
from uuid import uuid4


# 文件处理：把wav格式文件-->pcm文件, 便于AI接口识别
def get_file_content(filePath):
    cmd_str = f"ffmpeg -y -i {filePath} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filePath}.pcm"

    os.system(cmd_str)
    with open(f"{filePath}.pcm", 'rb') as fp:
        return fp.read()


# 语音识别，文件格式PCM
def audio2text(file_path):
    # 文件格式转换
    file_context = get_file_content(file_path)
    res = SPEECH_CLIENT.asr(file_context, "pcm", 16000, {"dev_pid": 1536})
    # 语音识别后的文本内容
    return res.get("result")[0]


# TTS语音合成
def text2audio(A):
    # 初始化
    res = SPEECH_CLIENT.synthesis(A, "zh", 1, VIOCE)
    file_name = f"{uuid4()}.mp3"
    file_path = os.path.join(AUDIO_CHAT_PATH, file_name)

    # 报错信息
    if type(res) == dict:
        pass

    # 文件写入AUDIO_CHAT_PATH文件夹
    with open(file_path, "wb") as f:
        f.write(res)

    return file_name


# 自然语言处理,NLP
def my_nlp(Q, toy_id):
    # 需求一：歌曲点播
    # Q = 我要听 / 我想听 / 请播放 + "洗澡歌" = 我要听洗澡歌
    # if "我要听" in Q or "我想听" in Q or "请播放" in Q:
    #     # 查询数据中所有歌曲数据
    #     for content in db.Content.find({}):
    #         # 当前歌曲匹配
    #         if content.get("title") in Q:
    #             return {
    #                 "from_user": "ai",
    #                 "music": content.get("music")
    #             }

    # 机器学习匹配结果，歌曲匹配
    music = my_nlp_content(Q)
    print(music,"////")
    # 匹配成功
    if music:
        return {"from_user": "ai", "music": music.get("music")}

    # 需求二：给好友发送消息，例如给老头子发送一条消息
    toy_info = db.Toys.find_one({"_id": ObjectId(toy_id)})
    friend_list = toy_info.get("friend_list")
    # print(friend_list,"33333")
    for friend in friend_list:
        # 好友尊称或者好友昵称
        if friend.get("friend_remark") in Q or friend.get("friend_nick") in Q:
            # 语音合成
            filename = text2audio(f"现在可以给{friend.get('friend_remark')}发送消息了")
            return {
                "from_user": friend.get("friend_id"),
                "chat": filename,
                "friend_type": friend.get("friend_type")
            }

    # 需求三：对接图灵机器人(预留端口)
    text_content = "我不知道你在说什么，请你在说一次"
    filename = text2audio(text_content)

    return {
        "from_user": "ai",
        "chat": filename
    }


