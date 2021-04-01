import os
import math
from protocol.message_type import MessageType
from protocol.transmission import send_message
from protocol.transmission import send_file


def handle(s, event_type, parameters):
    if event_type == MessageType.login:
        login(s, parameters)
    elif event_type == MessageType.signup:
        signup(s, parameters)
    elif event_type == MessageType.requireList:
        send_list(s, parameters)
    elif event_type == MessageType.download:
        send_book(s, parameters)
    elif event_type == MessageType.startRead:
        start_read(s, parameters)
    elif event_type == MessageType.requirePage:
        send_page(s, parameters)
    else:
        update_bookmark(s, parameters)


def login(s, parameters):
    parameters[0] = parameters[0].strip().lower()   # 删掉开头结尾的字符，并且转换为小写字母
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines()
        for user in users:
            user = user.split('|')
            if parameters[0] == user[0] and parameters[1] == user[1]:
                send_message(s, MessageType.loginSucc)
                print("用户名和密码正确，已发送登录成功信息！")
                return


def signup(s, parameters):
    parameters[0] = parameters[0].strip().lower()
    # 检查用户名是否被占用
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines()
        for user in users:
            user = user.split('|')
            if parameters[0] == user[0]:
                send_message(s, MessageType.usernameTaken)
                return

    # 用户名未被占用，添加到用户列表最后
    with open('./serve/users.txt', 'a+', encoding='utf-8') as f:
        f.write(parameters[0] + '|' + parameters[1] + '\n')
    send_message(s, MessageType.signupSucc)
    return


def send_list(s, parameters):
    book_list = os.listdir('./server/books')
    for i in range(len(book_list)):
        book_list[i] = book_list[i].strip('.txt')
    send_message(s, MessageType.bookList, book_list)
    print("已发送书籍列表！")
    return


def send_book(s, parameters):
    book_list = os.listdir('./server/books')
    for i in range(len(book_list)):
        book_list[i] = book_list[i].strip('.txt')
    if parameters not in book_list:
        send_message(s, MessageType.noBook)
        return
    send_file(s, './server/books/' + parameters + '.txt')
    print("书籍已发送！")
    return


def start_read(s, parameters):
    info = parameters.split('&')
    user_name = info[0]
    book_name = info[1]

    # 检查该书是否存在
    book_list = os.listdir('./server/books')
    for i in range(len(book_list)):
        book_list[i] = book_list[i].strip('.txt')
    if book_name not in book_list:
        send_message(s, MessageType.noBook)
        return

    # 查找书签
    page_num = 0    # 初始化书签为0
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines()
        for user in users:
            user = user.split('|')
            if user[0] == user_name:
                if book_name in user:
                    index = user.index(book_name)
                else:
                    index = -1
                if index != -1:
                    page_num = int(user[index+1])
                    break
    send_message(s, MessageType.pageNum, page_num)

    # 获得总页数和章节列表
    total_page = 0
    chapter = []
    chapter.append(['书名和作者', 0])
    i = 1
    with open('./server/books/' + book_name + '.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            s = ''
            s += line
            line = f.readline()
            while line:
                if line[0] == '#':
                    break
                s += line
                line = f.readline()
            total_page += math.ceil(len(s) / 1000)
            chapter.append([line[1: -1], total_page])
    send_message(s, MessageType.totalPage, total_page)
    send_message(s, MessageType.sendChapter, chapter)

    send_page(s, book_name + '&' + str(page_num))


def send_page(s, parameters):
    info = parameters.split('&')
    book_name = info[0]
    page_num = info[1]

    # 检查该书是否存在
    book_list = os.listdir('./server/books')
    for i in range(len(book_list)):
        book_list[i] = book_list[i].strip('.txt')
    if book_name not in book_list:
        send_message(s, MessageType.noBook)
        return

    # send a page
    book_path = './server/books/' + book_name + '.txt'
    with open(book_path, 'r', encoding='utf-8') as f:
        num = 0
        j = 0
        line = f.readline()
        while num <= page_num:
            s = ''
            if line:
                s += line
                line = f.readline()
                while line:
                    if line[0] == '#':
                        break
                    s += line
                    line = f.readline()
            if num + math.ceil(len(s) / 1000) - 1 < page_num:
                num += math.ceil(len(s) / 1000)
                continue
            elif num + math.ceil(len(s) / 1000) - 1 == page_num:
                j = 1000 * (math.ceil(len(s) / 1000) - 1)
                num += math.ceil(len(s) / 1000)
            else:
                j = 1000 * (page_num - num)
                num = page_num
                break
        send_message(s, MessageType.sendPage, s[j: j+1000])
    return


def update_bookmark(s, parameters):
    info = parameters.split('&')
    user_name = info[0]
    book_name = info[1]
    page_num = info[2]

    # 检查该书是否存在
    book_list = os.listdir('./server/books')
    for i in range(len(book_list)):
        book_list[i] = book_list[i].strip('.txt')
    if book_name not in book_list:
        send_message(s, MessageType.noBook)
        return

    # 修改书签
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.readline()
        for i in range(len(users)):
            user = users[i].split('|')
            if user[0] == user_name:
                if book_name in user:
                    index = user.index(book_name)
                    user[index+1] = str(page_num)
                    users[i] = '|'.join(user)
                else:
                    users[i] = users[i] + '|' + book_name + '|' + str(page_num)
                break

    with open('./server/users.txt', 'w', encoding='utf-8') as f:
        users = '\n'.join(users) + '\n'
        f.write(users)

    return


