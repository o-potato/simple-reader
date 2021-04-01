import enum


class MessageType(enum.IntEnum):
    # client action
    login = 1
    signup = 2
    requireList = 3
    download = 4
    startRead = 5
    requirePage = 6
    updateBookmark = 7

    # server action
    loginSucc = 11
    signupSucc = 12
    bookList = 13
    fileSize = 14
    sendPage = 15
    sendChapter = 16
    pageNum = 17
    totalPage = 18

    # failure
    loginFailed = 21    # 登录失败
    usernameTaken = 22  # 用户名已存在
    noBook = 23     # 查无此书
