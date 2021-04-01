import socket
import _thread
from protocol.transmission import recv_message
from protocol.message_type import MessageType
from server.handler import handle

HOST = '127.0.0.1'  # 标准回环地址（localhost）
PORT = 65432    # 监听的端口(非系统级端口：>1023)


def init_server():
    print("启动服务器！")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # 创建套接字
    s.bind((HOST, PORT))    # 将套接字绑定到地址（HOST， PORT）
    s.listen(5)     # 监听连接，设置最大连接数为5
    print("服务器在监听端口号：", PORT, "，等待客户端连接……")

    index = 0
    while True:
        if index >= 5:
            break
        conn, address = s.accept()  # 接收TCP连接，并返回（conn, address), 其中conn是新套接字，address是客户端地址
        index += 1
        _thread.start_new_thread(child_conn, (index, s, conn))  # 创建一个新的线程处理连接
    s.close()


def child_conn(index, s, conn):
    try:
        print("begin connection: ", index)
        conn.settimeout(6000)    # 120s无数据发送，超时退出
        while True:
            message_type, data = recv_message(conn)
            if not message_type:
                print("close connection: ", index)
                conn.close()
                _thread.exit()
                return
            print("Message Type: " + MessageType[message_type])
            print("From connection: ", index)
            print("Handling……")
            handle(conn, message_type, data)
    except socket.timeout:
        print("Time out!")

    print("Closing connection ", index)
    conn.close()    # 关闭连接
    _thread.exit()  # 退出线程
