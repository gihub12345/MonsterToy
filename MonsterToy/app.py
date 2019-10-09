from flask import Flask
from flask_cors import CORS

from day9520190719.MonsterToy.serv.friends import friend_bp
from day9520190719.MonsterToy.serv.content import content_bp
from day9520190719.MonsterToy.serv.devices import devices_bp
from day9520190719.MonsterToy.serv.uploader import uploader_bp
from day9520190719.MonsterToy.serv.user import user_bp

app = Flask(__name__)

# 注册蓝图，content_bp
app.register_blueprint(content_bp)
# 注册蓝图，user_bp
app.register_blueprint(user_bp)
# 注册蓝图，devices_bp
app.register_blueprint(devices_bp)
# 注册蓝图，friend_bp
app.register_blueprint(friend_bp)
# 注册蓝图，uploader_bp
app.register_blueprint(uploader_bp)

# 支持跨域请求
CORS(app)

if __name__ == '__main__':
    app.run("0.0.0.0", 9527, debug=True)

