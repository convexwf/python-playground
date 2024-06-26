# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : memobird-mail
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-03-09 11:11
# @UpdateTime : TODO


import base64
import time

import pymemobird

# 申请到的开发者编号
ACCESS_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
memobirdID = "XXXXXXX"
pymemobird.http_proxy = "http://open.memobird.cn/home/setuserbind"

if __name__ == "__main__":

    user = pymemobird.User(ACCESS_KEY, memobirdID)
    print("用户初始化...%s" % user.is_init())  # 验证初始化（可选）

    device = pymemobird.Device(memobirdID)
    print("设备初始化...%s" % device.is_init())  # 验证初始化（可选）

    device.bind_user(user)
    print("绑定用户...%s" % device.is_bind())  # 验证绑定状态（可选）

    paper = pymemobird.Paper(ACCESS_KEY)
    print("纸条初始化...%s" % paper.is_init())  # 验证初始化（可选）

    # 向纸条中添加文本和图片
    paper.add_text("Hello,world!你好呀！")
    pic = open("Logo.jpg", "rb")
    paper.add_pic(pic)
    pic.close()
    pic = open("Logo.jpg", "rb")
    pic_data = pic.read()
    pic_base64 = base64.b64encode(pic_data)
    paper.add_base64_pic(pic_base64)
    pic.close()

    # 打印纸条相关操作
    print("开始打印...%s" % paper.is_send())  # 验证纸条是否已经发送至打印列表
    device.print_paper(paper)  # 打印纸条
    print("开始打印...%s" % paper.is_send())  # 验证纸条是否已经发送至打印列表
    while paper.status() == "printing":
        time.sleep(1)
        paper.sync()  # 刷新纸条打印状态
        print("打印状态...%s" % paper.status())  # 获取纸条打印状态
