# 定义了消息发送和接收，文件发送和接收相关函数
# 消息发送和接收需要封装和解封装
# 文件发送和接收不需要封装和解封装

import socket

from protocol.encapsulation import pack_message
from protocol.encapsulation import unpack_message
from protocol.message_type import MessageType
from protocol.encapsulation import bytes_to_int
from struct import unpack
import os


# 消息的发送
def send_message(s, message_type, parameters=None):
    msg = pack_message(message_type, parameters)
    s.send(msg)
    return


# 消息的接收
def recv_message(s):
    try:
        msg_len = s.recv(4)
    except ConnectionError:
        conn_ok = False
        if msg_len == "" or len(msg_len) < 4:
            conn_ok = False
        if not conn_ok:
            print("连接失败！")
            return False
    length = unpack('!L', msg_len)[0]
    msg_type = s.recv(1)
    msg_type = unpack('!b', msg_type)
    msg = s.recv(length-1)
    if not msg:
        print("连接失败！")
        return False
    return unpack_message(msg_type, msg)


# 文件的发送
# 先发送文件大小，再传输文件内容
def send_file(s, file_path):
    send_message(s, MessageType.fileSize, os.path.getsize(file_path))

    with open(file_path, 'rb') as f:
        while True:
            filedata = f.read(1011)     # 1011 + 4 + 1 + 4 + 4 = 1024
            if not filedata:
                break;
            s.send(filedata)

    print("文件已发送！")
    return


# 文件接收
def recv_file(s, file_path):
    msg = recv_message(s)
    if msg['type'] == MessageType.noBook:
        print("查无此书！")
        return
    if msg['type'] is not MessageType.fileSize:
        print("未能获取文件大小，传输失败！")
        return

    filesize = msg['parameters']    # 要传输文件的大小
    try:
        with open(file_path, 'wb') as f:
            rest = filesize
            while True:
                filedata = s.recv(1024)
                if not filedata:
                    break
                f.write(filedata)
                rest -= len(filedata)
                if rest < 0:
                    break
        print("文件传输成功！")
    except Exception as e:
        print(e)
        print("文件传输失败！")
    return
