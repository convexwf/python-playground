# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/video_summary.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

json_root = "C:/Users/convexwf/Downloads/"

if __name__ == "__main__":
    json_file = os.path.join(json_root, "星期三 19 十一月 2025 - 001.json")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Total items:", len(data))
    text = ""
    for item in data:
        text += item["text"] + "\n"
    print("Total characters:", len(text))
    print("Sample text:", text)

    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://chat.cloudapi.vip/v1/",
    )

    response = client.responses.create(
        model="gpt-4o",
        # instructions="这是程序员面试中我回答面试官的发言整理，请你帮我总结我回答了哪些内容，猜测面试官可能想了解什么，重点关注一些技术细节，分点回答，千万不能有遗漏。",
        instructions="这是程序员面试中面试官的发言整理，请你帮我总结面试官问了哪些问题，千万不能有遗漏。",
        input=text,
    )

    print(response.output_text)
