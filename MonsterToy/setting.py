# mongodb数据库配置
from pymongo import MongoClient

m = MongoClient("127.0.0.1", 27017)
db = m["MonsterToy"]


# ---------------------------------------------------- #
# redis数据库配置
from redis import Redis

RDB = Redis("127.0.0.1", 6379)


# ---------------------------------------------------- #
# 文件存放位置路径配置
COVERT_PATH = "Cover"  # 专辑封面
MUSIC_PATH = "Music"  # 歌曲
QRCODE_PATH = "Qrcode"  # 玩具注册二维码
AUDIO_CHAT_PATH = "Audiofile"  # 语音聊天记录


# ---------------------------------------------------- #
# 返回前端的数据
RET = {
    "CODE": 0,
    "MSG": "注册成功！",
    "DATA": {}
}


# ---------------------------------------------------- #
# 连图二维码API
LT_URL = "http://qr.liantu.com/api.php?text=%s"


# ---------------------------------------------------- #
# BaiduAI配置
from aip import AipSpeech, AipNlp

""" 你的 APPID AK SK """
APP_ID = '16815061'
API_KEY = 'G9k256n6aeMRnfvS1paws50x'
SECRET_KEY = 'nCbbF44iUp6QrNvSgcYW0eo2EKKl4cvR'
SPEECH_CLIENT = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
NLP_CLIENT = AipNlp(APP_ID, API_KEY, SECRET_KEY)
VIOCE = {
    'vol': 5,
    "spd": 4,
    "pit": 5,
    "per": 4
}
