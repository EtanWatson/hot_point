import hashlib
import math

import time


def getASCP():
    t = int(math.floor(time.time()))
    e = hex(t).upper()[2:]
    m = hashlib.md5()
    m.update(str(t).encode(encoding='utf-8'))
    i = m.hexdigest().upper()

    if len(e) != 8:
        AS = '479BB4B7254C150'
        CP = '7E0AC8874BB0985'
        return AS, CP
    n = i[0:5]
    a = i[-5:]
    s = ''
    r = ''
    for o in range(5):
        s += n[o] + e[o]
        r += e[o + 3] + a[o]

    AS = 'A1' + s + e[-3:]
    CP = e[0:3] + r + 'E1'
    return AS, CP


def get_as_cp():
    zz = {}
    now = round(time.time())
    print
    now  # 获取计算机时间
    e = hex(int(now)).upper()[2:]  # hex()转换一个整数对象为十六进制的字符串表示
    print
    e
    i = hashlib.md5(str(int(now))).hexdigest().upper()  # hashlib.md5().hexdigest()创建hash对象并返回16进制结果
    if len(e) != 8:
        zz = {'as': "479BB4B7254C150",
              'cp': "7E0AC8874BB0985"}
        return zz
    n = i[:5]
    a = i[-5:]
    r = ""
    s = ""
    for i in range(5):
        s = s + n[i] + e[i]
    for j in range(5):
        r = r + e[j + 3] + a[j]
    zz = {
        'as': "A1" + s + e[-3:],
        'cp': e[0:3] + r + "E1"
    }
    return zz['as'], zz[cp]