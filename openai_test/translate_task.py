# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/translate_task.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-02-05 22:28
# @UpdateTime : 2025-02-05 22:28

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

# 你自定义的对话消息，举例是普通聊天格式
messages = [
    {"role": "system", "content": "你是一个帮助用户的助手。"},
]

if __name__ == "__main__":
    prompt_path = "input.md"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        messages.append({"role": "user", "content": content})

    json_path = "chapter_list.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        chapter_text = data["chapters"][0]["content"]
        chapter_split = chapter_text.replace("\n\n", "\n").split("\n")
        chapter = "\n\n".join(chapter_split[:2])

        messages.append({"role": "user", "content": chapter})

    print("Messages:", messages)

    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://chat.cloudapi.vip/v1/",
    )
    response = client.responses.create(
        model="gpt-4o",
        instructions="你是一个帮助用户的助手。",
        input=messages,
        # stream=True,
    )

    print("Response:", response.output_text)

    # text = ""
    # for chunk in response:
    #     if "choices" in chunk:
    #         delta = chunk["choices"][0]["delta"]
    #         if "content" in delta:
    #             text += delta["content"]

    # output_file = "output.md"
    # with open(output_file, "w+", encoding="utf-8") as f:
    #     f.write(text)
