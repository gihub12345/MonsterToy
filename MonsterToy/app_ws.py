import json
from flask import Flask, request, render_template
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WSGIServer
from geventwebsocket.websocket import WebSocket

ws_app = Flask(__name__)

# 用户的socket的字典，存储所有用户的websocket
user_socket_dict = {}


# ws的app应用
@ws_app.route("/app/<user_id>")
def app(user_id):
    # 在environ中获取wsgi.websocket服务
    app_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    # 存在用户服务请求，则存入字典
    if app_socket:
        user_socket_dict[user_id] = app_socket

    while True:
        # 接收？？？
        app_data = app_socket.receive()  # {to_user:"2",mus}
        print(app_data)
        try:
            # 把接收的信息转换成字典
            app_data_dict = json.loads(app_data)
            # 获取当前用户id
            to_user = app_data_dict.get("to_user")
            # 在字典中找到当前请求的用户
            usocket = user_socket_dict.get(to_user)
            # 对当前请求用户发送接收的信息
            usocket.send(app_data)
        except:
            continue


# ws的toy应用
@ws_app.route("/toy/<toy_id>")
def toy(toy_id):
    # 在environ中获取wsgi.websocket服务
    toy_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    # 存在用户服务请求，则存入字典
    if toy_socket:
        user_socket_dict[toy_id] = toy_socket

    while True:
        # 接收？？？
        toy_data = toy_socket.receive()
        print(toy_data)
        try:
            # 把接收的信息转换成字典
            toy_data_dict = json.loads(toy_data)
            # 获取当前用户id
            to_user = toy_data_dict.get("to_user")
            # 在字典中找到当前请求的用户
            usocket = user_socket_dict.get(to_user)
            # 对当前请求用户发送接收的信息
            usocket.send(toy_data)
        except:
            continue


# 请求玩具管理页面
@ws_app.route("/get_toy")
def get_toy():
    return render_template("WebToy.html")


if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0", 9528), ws_app, handler_class=WebSocketHandler)
    http_serv.serve_forever()
