# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : TIMRecordBackup
# @FileName : export_md.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-03-19 15:15
# @UpdateTime : 2022-03-19 15:15

import base64
import json
import os
import re
import sqlite3
import datetime
import time
import pandas as pd
import pytz

BASE_URL = 'http://0.0.0.0'
qq_self = '000000000'
db_path = 'data'

emoji_path = 'data/emoji/'

class exportHelper(object):

    def __init__(self):
        self.db = os.path.join(db_path, qq_self + ".db")
        self.db_cursor = sqlite3.connect(self.db).cursor()
        self.css_style = ['<style>\n'] + open('record.css', 'r', encoding='utf-8').readlines() + ['\n</style>\n']
        self.map_emoji()

    def close(self):
        self.db_cursor.close()

    def map_emoji(self):
        with open(emoji_path + 'face_config.json', encoding='utf-8') as fp:
            emojis = json.load(fp)
        self.emoji_map = {}
        for e in emojis['sysface']:
            if True:   ## 新版qq表情
                self.emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if len(e["EMCode"]) == 3:
                    self.emoji_map[e["AQLid"]] = str(int(e["EMCode"]) - 100)

    def export(self, time_interval):
        for idate in pd.date_range(time_interval[0], time_interval[1], freq='1D')[:-1]:
            OK, iresults = self.query(idate, idate+datetime.timedelta(days=1))
            idate_str = datetime.datetime.strftime(idate, "%Y-%m-%d")
            print('Solve date {}......'.format(idate_str))
            ipath = 'data/result/md/{}/record {}.md'.format(idate_str[:4], idate_str)
            if OK and len(iresults) > 0:
                os.makedirs(os.path.dirname(ipath), exist_ok=True)
                with open(ipath, 'w+', encoding='utf-8') as fp:
                    fp.writelines(self.css_style)
                    fp.write('\n'.join(iresults))

    def add_image(self, msgdata):
        while True:
            obj = re.search('\[图片消息\]\((Cache_.*?)\)', msgdata)
            if obj:
                pic_dir = obj.group(1)[-3:]
                pic_name = obj.group(1)+ '.png'
                pic_filepath = os.path.join(db_path, 'chatimg_png', pic_dir, pic_name)
                pic_url = "{}/chatimg/{}/{}".format(BASE_URL, pic_dir, pic_name)
                if not os.path.exists(pic_filepath):
                    pic_html = '[图片失效]'
                elif os.path.getsize(pic_filepath) > 100 * 1024:
                    pic_html = '<a href="{}">图片查看</a>'.format(pic_url)
                else:
                    pic_html = '<a href="{}"><img src="{}" alt="[图片请求失败]"></a>'.format(pic_url, pic_url)
                msgdata = msgdata.replace(obj.group(0), pic_html)
            else:
                break
        return msgdata

    def get_base64_from_pic(self, path):
        with open(path, "rb") as image_file:
            return (b'data:image/png;base64,' + base64.b64encode(image_file.read())).decode("utf-8")

    def add_emoji(self, msg):
        pos = msg.find('\x14')
        while pos != -1:
            lastpos = pos
            num = ord(msg[pos + 1])
            if str(num) in self.emoji_map:
                index = self.emoji_map[str(num)]

                if True: ## 新版qq表情
                    filename = "new/s" + index + ".png"
                else:
                    filename = "old/" + index + ".gif"

                emotion_path = os.path.join(emoji_path, filename)
                emoticon_path = self.get_base64_from_pic(emotion_path)
                msg = msg.replace(msg[pos:pos + 2], '<img src="{}" alt="{}" />'.format(emoticon_path, index))
            else:
                msg = msg.replace(msg[pos:pos + 2], '[emoji:{}]'.format(str(num)))
            pos = msg.find('\x14')
            if pos == lastpos:
                break
        return msg

    def transform_qq(self, qq_number, sendtime):
        if qq_number == 735165920:
            return '<PB>卜卜  {} </PB>'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sendtime)))
        else:
            return '<PA>兔兔  {} </PA>'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sendtime)))

    def transform_msg(self, msgtype, msgdata):
        # print(msgtype, msgdata)
        if msgtype == -2000 or msgtype == -1035:
            msgdata = self.add_image(msgdata)
        msgdata = self.add_emoji(msgdata)
        return '<rc>{}</rc>'.format(msgdata)

    def query(self, start_date, end_date):
        # print(start_date.replace(tzinfo=pytz.timezone('Asia/Shanghai')).timestamp(), start_date.timestamp())
        start_ts = int(start_date.replace(tzinfo=pytz.timezone('Asia/Shanghai')).timestamp())
        end_ts = int(end_date.replace(tzinfo=pytz.timezone('Asia/Shanghai')).timestamp())
        query_sql = 'select msgdata, msgtype, senderId, senderName, time '\
                        'from friend_948188388 where time between {} and {} order by time'.format(start_ts, end_ts)

        try:
            results = []
            query_cursor = self.db_cursor.execute(query_sql)
            for row in query_cursor:
                msgdata, msgtype, sender_id, _, send_time = \
                                    row[0], row[1], row[2], row[3], row[4]
                results.append(self.transform_qq(sender_id, send_time))
                results.append(self.transform_msg(msgtype, msgdata))
            return True, results
        except Exception:
            return False, '记录查询失败'

if __name__ == '__main__':
    helper = exportHelper()
    helper.export(['201901010000', '202203180000'])
    helper.close()
