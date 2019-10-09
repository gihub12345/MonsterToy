# 怎么存储离线未读消息
# {
#     "user_id":{
#         "from_id1":1,
#         "from_id2":6,
#         "from_id3":3,
#         "from_id4":4
#     }
# }

# 获取一条消息字典转换成json字符串
# dp = json.dumps({"user_1":1})
# redis.set(to_user,dp)


import json
from day9520190719.MonsterToy.setting import RDB


# 存储未读消息
def set_redis(to_user, from_user):
    # 获取接收信息的字典
    to_user_json = RDB.get(to_user)
    # 存在聊天记录的未读消息
    if to_user_json:
        # 获取当前玩具的未读消息
        to_user_dict = json.loads(to_user_json)  # type: dict

        # 方式一
        # 存在未读消息时，追加1条
        # if to_user_dict.get(from_user):
        #     to_user_dict[from_user] += 1
        # else:
        #     # 添加1
        #     to_user_dict[from_user] = 1

        # 方式二
        to_user_dict[from_user] = to_user_dict.setdefault(from_user, 0) + 1
        # 新的维未读消息转换成json字符串
        to_user_json = json.dumps(to_user_dict)
    else:
        # 新建一个未读消息的数据字典
        to_user_json = json.dumps({from_user: 1})

    # 存入redis数据库
    RDB.set(to_user, to_user_json)


# 获取单个用户的未读消息
def get_redis(to_user, from_user):
    to_user_json = RDB.get(to_user)

    to_user_dict = json.loads(to_user_json)

    # 消息初始值为0
    count = 0

    if to_user_dict:
        # 获取当前用户未读消息条数
        count = to_user_dict.get(from_user)
        # 当前用户的消息不存在
        if not count:
            count = 0
        # 读取当前消息后，消息清零
        to_user_dict[from_user] = 0
        # dumps操作，from_user = 0
        to_user_json = json.dumps(to_user_dict)
    else:
        # 用户不存在未读消息
        to_user_json = json.dumps({from_user: 0})

    RDB.set(to_user, to_user_json)

    return count


# 每次点击获取不同用户的未读消息
def get_redis_toy(to_user, from_user):
    # 获取redis数据库中当前用户的所有
    to_user_json = RDB.get(to_user)
    # 数据存在
    if to_user_json:
        to_user_dict = json.loads(to_user_json)
        # 获取到未读消息条数
        count = to_user_dict.pop(from_user, 0)
        # 如果当前用户没有当前好友的未读消息
        if count == 0:
            # 遍历获取下一条好友的未读消息
            for k, v in to_user_dict.items():
                if v:
                    # 获取好友ID
                    from_user = k
                    # 未读消息条数
                    count = v

        # 当前好友消息字典的未读消息条数清零
        to_user_dict[from_user] = 0

        # 格式转换
        to_user_json = json.dumps(to_user_dict)
    else:
        to_user_json = json.dumps({from_user: 0})
        count = 0

    # 重新写入redis数据库
    RDB.set(to_user, to_user_json)

    # 返回消息条数，及当前好友ID
    return count, from_user


# 获取所有未读消息
def get_all_redis(to_user):
    to_user_json = RDB.get(to_user)

    # redis数据库中存在未读数据
    if to_user_json:
        # json格式 -> dict格式
        to_user_dict = json.loads(to_user_json)
        # 未读消息条数求和
        to_user_dict["count"] = sum(to_user_dict.values())
    else:
        # 否则消息默认为0
        to_user_dict = {"count": 0}

    return to_user_dict


