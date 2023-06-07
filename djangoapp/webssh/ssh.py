#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/7 00:35
# @Author  : tomoncle
# @Site    : https://github.com/tomoncle
# @File    : ssh.py
# @Software: PyCharm

import hashlib
import json
import random
import time
from threading import Thread

import paramiko
from channels.generic.websocket import WebsocketConsumer

from .models import Server


def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    if pkey_file:
        with open(pkey_file) as fo:
            try:
                pkey = pkeyobj.from_private_key(fo, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)


def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()


class StreamConsumer(object):
    def __init__(self, websocket):
        self.websocket = websocket

    def connect(self, host_ip, host_port, sys_user_name, sys_user_passwd, term='xterm', cols=140, rows=50):
        # 实例化SSHClient
        ssh_client = paramiko.SSHClient()
        # 当远程服务器没有本地主机的密钥时自动添加到本地，这样不用在建立连接的时候输入yes或no进行确认
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # 连接ssh服务器，这里是以账号密码方式进行确认
            ssh_client.connect(host_ip, host_port, sys_user_name, sys_user_passwd, timeout=10)
            print("连接成功")
        except Exception as e:
            message = str(e)
            # self.websocket.send是服务端给客户端发送消息
            self.websocket.send(message)
            print("连接失败")
            return False
        # 打开ssh通道，建立长连接
        transport = ssh_client.get_transport()
        # 建立会话session
        self.ssh_channel = transport.open_session()
        # 获取终端，并设置term和终端大小,width终端宽度，height终端高度
        self.ssh_channel.get_pty(term=term, width=cols, height=rows)
        # 激活终端，这样就可以正常登录了
        self.ssh_channel.invoke_shell()
        msg = f"开始连接到{sys_user_name}@{host_ip} \r\n"
        self.websocket.send(msg)
        for i in range(2):
            mess = self.ssh_channel.recv(1024).decode('utf-8', 'ignore')
            message = json.dumps({'flag': 'success', 'message': mess})
            self.send_to_ws_mes(message)

    # 断开websocket和关闭ssh通道
    def close(self):
        try:
            self.websocket.close()
            self.ssh_channel.close()
        except Exception as e:
            pass

    # 发送消息到ws
    def send_to_ws_mes(self, event):
        # 字符串转换字典
        text_data = json.loads(event)
        message = text_data['message']
        self.websocket.send(message)

    # 从websocket接收的数据发送到ssh
    def _ws_to_ssh(self, data):
        try:
            self.ssh_channel.send(data)
        except OSError as e:
            self.close()

    # ssh返回的数据输出给websocket
    def _ssh_to_ws(self):
        try:
            while not self.ssh_channel.exit_status_ready():
                # 需要转码为utf-8形式
                data = self.ssh_channel.recv(1024).decode('utf-8')
                message = {'flag': 'success', 'message': data}
                if len(data) != 0:
                    self.send_to_ws_mes(json.dumps(message))
                else:
                    break
        except Exception as e:
            message = {'flag': 'error', 'message': str(e)}
            self.send_to_ws_mes(json.dumps(message))
            self.close()

    def shell(self, data):
        Thread(target=self._ws_to_ssh, args=(data,)).start()
        Thread(target=self._ssh_to_ws).start()

    # 前端传过来的数据会加个flag，如果flag是resize，则调用resize_pty方法来动态调整窗口的大小，否则就正常调用执行命令的方法
    def resize_pty(self, cols, rows):
        self.ssh_channel.resize_pty(width=cols, height=rows)


# 继承WebsocketConsumer 类
class SSHConsumer(WebsocketConsumer):
    def connect(self):
        # 有客户端来向后端发起websocket连接的请求时，自动触发
        host_info = self.scope["query_string"].decode()
        self.host_ip = host_info.split('&')[0].split('=')[1]
        self.host_name = host_info.split('&')[1].split('=')[1]
        self.host_port = host_info.split('&')[2].split('=')[1]
        self.sys_user_name = host_info.split('&')[3].split('=')[1]
        self.sys_user_passwd = host_info.split('&')[4].split('=')[1]
        # accept表示服务端允许和客户端创建连接.
        self.accept()

        self.ssh = StreamConsumer(websocket=self)
        self.ssh.connect(self.host_ip, self.host_port, self.sys_user_name, self.sys_user_passwd)

    def disconnect(self, close_code):
        # 客户端与服务端断开连接时，自动触发（客户端断开，服务端也得断开）
        self.ssh.close()

    def receive(self, text_data=None, bytes_data=None):
        # 浏览器基于websocket向后端发送数据，自动触发接收消息。
        # text_data是从客户端端(websocket)接收到的消息
        text_data = json.loads(text_data)  # str转换为dict
        if text_data.get('flag') == 'resize':  # 如果为resize是改变终端通道的大小
            self.ssh.resize_pty(cols=text_data['cols'], rows=text_data['rows'])
        else:  # 否则正常执行命令
            data = text_data.get('entered_key', '')
            self.ssh.shell(data=data)


class SSHWebSocket(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ssh = None

    def connect(self):
        # 有客户端来向后端发起websocket连接的请求时，自动触发
        args = self.scope["query_string"].decode()
        server_id = args.split("=")[1]
        if not server_id or len(server_id) < 32:
            print("Server ID 不合法！")
            return

        server = Server.objects.get(sid=server_id)
        # accept表示服务端允许和客户端创建连接.
        self.accept()
        self.ssh = StreamConsumer(websocket=self)
        self.ssh.connect(server.host, server.port, server.user, server.password)

    def disconnect(self, close_code):
        # 客户端与服务端断开连接时，自动触发（客户端断开，服务端也得断开）
        if not self.ssh:
            return
        self.ssh.close()

    def receive(self, text_data=None, bytes_data=None):
        if not self.ssh:
            return
        # 浏览器基于 websocket 向后端发送数据，自动触发接收消息。text_data是从客户端端(websocket)接收到的消息
        # str转换为dict
        text_data = json.loads(text_data)
        if text_data.get('flag') == 'resize':  # 如果为resize是改变终端通道的大小
            self.ssh.resize_pty(cols=text_data['cols'], rows=text_data['rows'])
        else:  # 否则正常执行命令
            data = text_data.get('entered_key', '')
            self.ssh.shell(data=data)
