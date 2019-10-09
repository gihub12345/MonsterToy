from day9520190719.MonsterToy.setting import LT_URL, QRCODE_PATH, db

import requests
import os
import time
import hashlib
from uuid import uuid4

device_list = []

for i in range(10):
    # 生成随机字符串
    str1 = f"{uuid4()}{time.time()}{uuid4()}".encode("utf-8")
    # md5加密
    qr_str = hashlib.md5(str1).hexdigest()
    print(qr_str)

    # 生成一个字典数据结构
    device_info = {"device_key": qr_str}
    # 把字典对象放入列表
    device_list.append(device_info)

    # 通过二维码api生成二维码
    res = requests.get(LT_URL % qr_str)
    # 二维码文件存放位置拼接
    qrfile_path = os.path.join(QRCODE_PATH, f"{qr_str}.jpg")
    # 文件写入
    with open(qrfile_path, "wb") as f:
        f.write(res.content)

# 把二维码列表存储至数据库
db.Devices.insert_many(device_list)
