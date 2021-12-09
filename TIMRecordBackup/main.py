# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : TIMRecordBackup
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-03-20 15:15
# @UpdateTime : 2022-03-20 15:15

from datetime import datetime
import hashlib
import sqlite3
import time
import os
import traceback
import json
import base64
import shutil
from PIL import Image, ImageFile
from io import BytesIO
from proto.RichMsg_pb2 import PicRec
from proto.RichMsg_pb2 import Elem
from proto.RichMsg_pb2 import Msg
ImageFile.LOAD_TRUNCATED_IMAGES = True

qq_self = '000000000'
friend_target = ['000000000', '000000000', '000000000', '000000000']
troop_target = ['000000000', '000000000', '000000000', '000000000', '000000000']
last_date = int(datetime.strptime('20211212', '%Y%m%d').timestamp())
db_path = 'data/20220313'
save_path = 'data'
save_png = True  ## 是否要将涉及记录中的图片转储为 png

_crc64_init = False
_crc64_table = [0] * 256


## 记录解码，并针对不同类型的消息进行处理
def decrypt(key, data, msg_type=-1000):
    msg = b''
    if type(data) == bytes:
        msg = b''
        for i in range(0, len(data)):
            msg += bytes([data[i] ^ ord(key[i % len(key)])])
    elif type(data) == str:
        msg = ''
        for i in range(0, len(data)):
            msg += chr(ord(data[i]) ^ ord(key[i % len(key)]))
        return msg

    if msg_type == -1000 or msg_type == -1051:  ## 普通文字消息
        try:
            return msg.decode('utf-8')
        except Exception:
            return '[无效文字消息]'
    elif msg_type == -1049:                     ## 回复的文字消息
        return '[回复消息]' + msg.decode('utf-8')
    elif msg_type == -2000:                     ## 图片消息
        pic_file =  decode_pic(msg)
        if pic_file:
            return '[图片消息](' + pic_file + ')'
        return '[图片缺失]'
    elif msg_type == -1035:                     ## 混合图片文字消息
        doc = Msg()
        doc.ParseFromString(msg)
        message = ''
        for elem in doc.elems:
            if elem.picMsg:
                pic_file =  decode_pic(elem.picMsg)
                if pic_file:
                    message += ('[图片消息](' + decode_pic(elem.picMsg)) + ')'
                else:
                    message += '[图片缺失]'
            else:
                message += elem.textMsg.decode('utf-8')
        return message
    elif msg_type == -2011:                     ## 转发分享消息
        # print(msg.decode('utf-8'))
        # try:
        #     return '[转发消息]' + str(msg[9:250].decode('utf-8'))  # 7:321
        # except Exception:
        return '[转发消息与分享]'
    elif msg_type == -2007:
        return '[自定义表情]'
    elif msg_type == -2009:
        return '[语音或视频通话]'
    elif msg_type == -5012 or msg_type == -5018:
        return '[戳一戳]'
    elif msg_type == -2005:
        return '[文件分享]'
    elif msg_type == -2002:
        return '[语音消息]'
    elif msg_type == -2022:
        return '[短视频]'
    elif msg_type == -5008:
        return '[分享卡片]'
    else:
        return '[unknown msg_type {}]'.format(msg_type)

## 用于图片编解码
def crc64(s):
    global _crc64_init
    if not _crc64_init:
        for i in range(256):
            bf = i
            for j in range(8):
                if bf & 1 != 0:
                    bf = bf >> 1 ^ -7661587058870466123
                else:
                    bf >>= 1
            _crc64_table[i] = bf
        _crc64_init = True
    v = -1
    for i in range(len(s)):
        v = _crc64_table[(ord(s[i]) ^ v) & 255] ^ v >> 8
    return v

## 从消息记录获取图片 url，并得到对应图片
def decode_pic(data):

    doc = PicRec()
    doc.ParseFromString(data)
    pic_url = 'chatimg:' + doc.md5
    pic_name = hex(crc64(pic_url))
    pic_file = 'Cache_' + pic_name.replace('0x', '')
    src_filename = os.path.join(db_path, 'chatimg', pic_file[-3:], pic_file)
    dst_filename = os.path.join(save_path, 'chatimg', pic_file[-3:], pic_file)
    img_filename = os.path.join(save_path, 'chatimg_png', pic_file[-3:], pic_file + '.png')

    if not os.path.exists(src_filename):
        # print('{} Not exists'.format(src_filename))
        return

    if not os.path.exists(dst_filename):
        os.makedirs(os.path.dirname(dst_filename), exist_ok=True)
        shutil.copyfile(src_filename, dst_filename)

    if save_png and not os.path.exists(img_filename):
        os.makedirs(os.path.dirname(img_filename), exist_ok=True)
        transformBase64Pic(dst_filename, img_filename)

    return pic_file

## 将 cache_XXX 通过 base64 编码得到图像数据
def transformBase64Pic(src_path, dst_path):
    # print(src_path)
    with open(src_path, "rb") as image_file:
        image_data = BytesIO(image_file.read())
    img = Image.open(image_data)
    if dst_path:
        img.save(dst_path)

class TIMOuput(object):

    def __init__(self, qq_number, friend_or_troop) -> None:
        super().__init__()

        self.key = self.getKey()  # 解密用的密钥
        self.db_sursor, self.slowdb_cursor = self.getDb()  # 获取聊天记录 db
        self.qq_number = qq_number
        self.friend_or_troop = friend_or_troop
        self.number_to_name = {} # qq 号到昵称的映射
        if self.friend_or_troop == 'friend':
            self.get_friends()
        else:
            self.get_troop_members()

    ## 获取秘钥文件 (files/kc，里面是一串数字)
    def getKey(self):
        kc_path = os.path.join(db_path, "files", "kc")
        return open(kc_path, "r").read()

    ## 获取 db 和 slow_db
    def getDb(self):
        db = os.path.join(db_path, "databases", qq_self + ".db")
        db_cursor = sqlite3.connect(db).cursor()
        slow_db = os.path.join(db_path, "databases", "slowtable_" + qq_self + ".db")
        slowdb_cursor = sqlite3.connect(slow_db).cursor()
        return db_cursor, slowdb_cursor

    ## 执行 sql 语句
    def executeSQL(self, cmd):
        cursors = []
        # slowtable might not contain related message, so just skip it
        try:
            cursors.append(self.slowdb_cursor.execute(cmd))
        except:
            pass
        cursors.append(self.db_sursor.execute(cmd))
        return cursors

    ## 查找好友 qq 号以及昵称
    def get_friends(self):
        cmd = "SELECT uin, name FROM Friends"
        cursors = self.executeSQL(cmd)
        for cs in cursors:
            for row in cs:
                num = decrypt(self.key, row[0])
                name = decrypt(self.key, row[1])
                if num == self.qq_number or num == qq_self:
                    self.number_to_name[num] = name

    ## 查找群友 qq 号以及昵称
    def get_troop_members(self):
        cmd = "SELECT troopuin, memberuin, friendnick FROM TroopMemberInfo"
        cursors = self.executeSQL(cmd)
        for cs in cursors:
            for row in cs:
                if decrypt(self.key, row[0]) != self.qq_number:
                    continue
                num = decrypt(self.key, row[1])
                name = decrypt(self.key, row[2])
                self.number_to_name[num] = name

    ## 抽取消息记录
    def getMessage(self):
        target = self.qq_number.encode("utf-8")
        md5num = hashlib.md5(target).hexdigest().upper()
        cmd = 'select msgData, msgtype, senderuin, time, msgseq, msgId, msgUid, shmsgseq, uniseq, extStr '\
                'from mr_{}_{}_New where time >= {} order by time'.format(self.friend_or_troop, md5num, last_date)
        # cmd = 'select msgData, msgtype, senderuin, time, msgseq, msgId, msgUid, shmsgseq, uniseq, extStr '\
        #         'from mr_{}_{}_New order by time'.format(self.friend_or_troop, md5num)
        print(cmd)
        cursors = self.executeSQL(cmd)

        for cs in cursors:
            for row in cs:
                msgdata, msgtype, senderuin, timest, msgseq, msgId, msgUid, shmsgseq, uniseq, extstr = \
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                if not msgdata:
                    continue
                send_qq  = decrypt(self.key, senderuin)
                if send_qq not in self.number_to_name:
                    send_qq = 0
                    send_name = '佚名'
                else:
                    send_name = self.number_to_name[send_qq]
                sendtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timest))
                msg_decode = decrypt(self.key, msgdata, msgtype)
                extstr_decode = decrypt(self.key, extstr, msg_type=-1000)

                # pos = msg_decode.find('\x14')
                # if pos == -1:
                #     continue
                # if msgtype!=-2011:
                #     continue
                print(send_qq, msgtype, uniseq, sendtime, msg_decode)
                self.log('{} {} {} {} {}'.format(send_qq, msgtype, uniseq, sendtime, msg_decode))
                # time.sleep(0.1)
                yield [msg_decode, msgtype, msgseq, msgId, msgUid, timest,
                        send_qq, send_name,
                        shmsgseq, uniseq, extstr_decode]

    ## 转储消息记录
    def saveMessage(self):
        table_name = '{}_{}'.format(self.friend_or_troop, self.qq_number)

        query_sql = 'SELECT name FROM SQLITE_MASTER WHERE name="{}"'.format(table_name)
        create_sql = 'CREATE TABLE {} ('\
            '_id INTEGER PRIMARY KEY AUTOINCREMENT,'\
            'msgdata TEXT,'\
            'msgtype INTEGER,'\
            'msgseq INTEGER,'\
            'msgId INTEGER,'\
            'msgUid INTEGER,'\
            'time INTEGER,'\
            'senderId INTEGER,'\
            'senderName TEXT,'\
            'shmsgseq INTEGER,'\
            'uniseq INTEGER,'\
            'extStr TEXT,'\
            'UNIQUE(time,senderId,msgdata,shmsgseq,msgseq) ON CONFLICT REPLACE)'.format(table_name)
            # 'UNIQUE(time,senderId,msgdata,shmsgseq,msgseq) ON CONFLICT IGNORE)'.format(table_name)
        index_sql = 'CREATE INDEX {}_idx ON {}(time, _id)'.format(table_name, table_name)
        insert_sql = 'INSERT INTO {} (msgdata, msgtype, msgseq, msgId, msgUid, time,'\
            'senderId,senderName,shmsgseq,uniseq,extStr) VALUES (?,?,?,?,?,?,?,?,?,?,?)'.format(table_name)


        dst_db = os.path.join(save_path, qq_self + ".db")
        dst_conn = sqlite3.connect(dst_db)
        dst_cursor = dst_conn.cursor()
        table_exist = len(list(dst_cursor.execute(query_sql))) > 0
        if not table_exist:
            dst_cursor.execute(create_sql)
            dst_cursor.execute(index_sql)
            dst_conn.commit()
        for message in self.getMessage():
            dst_cursor.execute(insert_sql, message)
        dst_conn.commit()
        dst_conn.commit()
        dst_conn.close()

    def log(self, info):
        log_path = os.path.join(save_path, 'log', 'chat_{}.log'.format(self.qq_number))
        with open(log_path, 'a+', encoding='utf-8') as fp:
            fp.write(info + '\n')



if __name__ == '__main__':

    for file_dir in os.listdir(os.path.join(save_path, 'chatimg')):
        file_xxx = os.path.join(save_path, 'chatimg', file_dir)
        for file in os.listdir(file_xxx):
            file_yyy = os.path.join(file_xxx, file)
            file_dst = os.path.join(save_path, 'chatimg_png', file_dir, file+'.png')

            print(file_yyy, '\t---->>>>\t', file_dst)
            if save_png and not os.path.exists(file_dst):
                os.makedirs(os.path.dirname(file_dst), exist_ok=True)
                transformBase64Pic(file_yyy, file_dst)

    # for friend in friend_target[:]:
    #     solver = TIMOuput(friend, 'friend')
    #     solver.saveMessage()

    # for troop in troop_target[:]:
    #     solver = TIMOuput(troop, 'troop')
    #     solver.saveMessage()



    # solver.get_friends()
    # solver.get_troop_members()

    # import datetime
    # start_date = '2020-08-12 10:00'
    # end_date = '2020-08-12 15:00'
    # start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
    # end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
    # # if end_time - start_time > datetime.timedelta(hours=24):
    # #     return
    # start_ts = start_time.timestamp()
    # end_ts = end_time.timestamp()
    # print(start_ts, end_ts)

