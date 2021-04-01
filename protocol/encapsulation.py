# 由于socket只能传输bytes类型数据，故要传送的数据应首先转换成bytes类型，
# 进行第一次封装；第一次封装结果作为要传送的message进行第二次封装

from struct import pack
from struct import unpack


# int/str/list to bytes
# | -- 1 Byte DataType -- | -- 4 Byte DataLength -- | -- Data -- |

# DataType:
# int  -- 1
# str  -- 2
# list -- 3

def int_to_bytes(data):
    s = str(data)
    body = str.encode(s)
    return bytes([1]) + pack('!L', len(body)) + body


def str_to_bytes(data):
    body = str.encode(data)
    return bytes([2]) + pack('!L', len(body)) + body


def list_to_bytes(data):
    if len(data) == 0:
        body = str.encode("")
        return bytes([3]) + pack('!L', len(body)) + body
    s = str(data[0])
    for i in range(1, len(data)):
        s += ('&' + str(data[i]))
    body = str.encode(s)
    return bytes([3]) + pack('!L', len(body)) + body


def obj_to_bytes(obj):
    if type(obj) is list:
        return list_to_bytes(obj)
    if type(obj) is int:
        return int_to_bytes(obj)
    if type(obj) is str:
        return str_to_bytes(obj)


# message encapsulation
# | -- 4 Bytes MessageLength -- | -- 1 Bytes MessageType -- | -- Message -- |
# MessageLength = length of MessageType + length of Message
# 所以先封装 MessageType 和 Message, 再计算总长度并添加到头部

def pack_message(message_type, parameters):    # 可完成两层封装
    # res = bytes([message_type.value])
    res = pack('!b', message_type)
    print(obj_to_bytes(parameters))
    res += obj_to_bytes(parameters)
    print(pack('!L', len(res)) + res)
    return pack('!L', len(res)) + res


# bytes to int/str/list
# | -- 1 Byte DataType -- | -- 4 Byte DataLength -- | -- Data -- |

def bytes_to_int(data):
    return int.from_bytes(data, 'big')


def bytes_to_str(data):
    return bytes.decode(data)


def bytes_to_list(data):
    s = bytes_to_str(data)
    s.split("&")
    return s


def unpack_data(data):
    data_type = int.from_bytes(data[0], 'big')     # get DataType
    data_len = int.from_bytes(data[1:4], 'big')      # get DataLength
    if data_type == 1:
        return bytes_to_int(data[5:])
    elif data_type == 2:
        return bytes_to_str(data[5:])
    else:
        return bytes_to_list(data[5:])


# get message
# | -- 4 Bytes MessageLength -- | -- 1 Bytes MessageType -- | -- Message -- |

def unpack_message(message_type, message):
    # message_len = bytes_to_int(message[0:3])
    # message_type = unpack('!b', message[0])[0]
    body = unpack_data(message)
    return {'type': message_type, 'parameters': body}
