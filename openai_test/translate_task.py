# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/translate_task.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-02-05 22:28
# @UpdateTime : 2025-03-29 17:17

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

ENGLISH_TOKEN_LIMIT = 3000
JANPANESE_TOKEN_LIMIT = 3000

init_prompt = [
    {"role": "system", "content": "你是一个热心而且专业的助手。"},
]


def connect_to_openai(messages):
    """
    Connects to OpenAI API using the API key from environment variables.
    """
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://chat.cloudapi.vip/v1/",
    )
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
    )
    # log
    with open("openai_response.log", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(response.to_dict(), ensure_ascii=False) + "\n")
    return response.output_text.strip()


def check_openai_connection():
    """
    Checks if the OpenAI API connection is working.
    """
    reply = connect_to_openai(
        messages=init_prompt
        + [
            {
                "role": "user",
                "content": "Translate this text to Chinese: Hello, how are you?",
            }
        ]
    )
    print("Reply:", reply)


def translate_english_text(text):
    """
    Translates English text to Chinese.

    Args:
        text (str): The English text to translate.

    Returns:
        str: The translated Chinese text.
    """
    messages = init_prompt.copy()
    english_prompt_path = "enlish_prompt.md"
    if os.path.exists(english_prompt_path):
        with open(english_prompt_path, "r", encoding="utf-8") as f:
            english_prompt = f.read()
        messages.append({"role": "user", "content": english_prompt})

    text_split = text.replace("\n\n", "\n").split("\n")

    chunk_list = []
    for line in text_split:
        if (
            len(chunk_list) == 0
            or len(chunk_list[-1]) + len(line) > ENGLISH_TOKEN_LIMIT
        ):
            chunk_list.append(line)
        else:
            chunk_list[-1] += "\n\n" + line

    translate_result = ""
    for chunk in chunk_list:
        print(f"Translating chunk of length {len(chunk)}")
        chunk_messages = messages + [{"role": "user", "content": chunk}]
        reply = connect_to_openai(messages=chunk_messages)
        translate = reply[11:-3].strip()
        while translate.endswith("to be continued"):
            translate_result += translate[: -len("to be continued")].strip() + "\n\n"
            chunk_messages.append({"role": "assistant", "content": reply})
            chunk_messages.append({"role": "user", "content": "continue"})
            reply = connect_to_openai(messages=chunk_messages)
            translate = reply[11:-3].strip()
        if translate.endswith("fin"):
            translate = translate[: -len("fin")].strip()
        translate_result += translate + "\n\n"

    return translate_result


def translate_japanese_text(text):
    """
    Translates Japanese text to Chinese.

    Args:
        text (str): The Japanese text to translate.

    Returns:
        str: The translated Chinese text.
    """
    messages = init_prompt.copy()
    japanese_prompt_path = "japanese_prompt.md"
    if os.path.exists(japanese_prompt_path):
        with open(japanese_prompt_path, "r", encoding="utf-8") as f:
            japanese_prompt = f.read()
        messages.append({"role": "user", "content": japanese_prompt})

    text_split = text.replace("\n\n", "\n").split("\n")
    chunk_list = []
    for line in text_split:
        if (
            len(chunk_list) == 0
            or len(chunk_list[-1]) + len(line) > JANPANESE_TOKEN_LIMIT
        ):
            chunk_list.append(line)
        else:
            chunk_list[-1] += "\n\n" + line

    translate_result = ""
    for chunk in chunk_list:
        print(f"Translating chunk of length {len(chunk)}")
        chunk_messages = messages + [{"role": "user", "content": chunk}]
        reply = connect_to_openai(messages=chunk_messages)
        translate = reply[11:-3].strip()
        while translate.endswith("to be continued"):
            translate_result += translate[: -len("to be continued")].strip() + "\n\n"
            chunk_messages.append({"role": "assistant", "content": reply})
            chunk_messages.append({"role": "user", "content": "continue"})
            reply = connect_to_openai(messages=chunk_messages)
            translate = reply[11:-3].strip()
        if translate.endswith("fin"):
            translate = translate[: -len("fin")].strip()
        translate_result += translate + "\n\n"

    return translate_result


if __name__ == "__main__":
    # test_path = "tmp/The Economist/The Economist 2025-07-05.json"
    # if not os.path.exists(test_path):
    #     print(f"Test file does not exist: {test_path}")
    #     exit(1)
    # with open(test_path, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # chapter_text = data["chapters"][70]["content"]
    # print(f"Chapter text length: {len(chapter_text)}")
    # print(f"Chapter text: {chapter_text[:100]}...")
    # translate_english_text(chapter_text)

    # with open("translated_input.md", "w+", encoding="utf-8") as f:
    #     f.write(chapter_text)

    test_path = "tmp/douban_topic_list.json"
    if not os.path.exists(test_path):
        print(f"Test file does not exist: {test_path}")
        exit(1)
    with open(test_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    topic_text = data["topics"][2]["text"]
    print(f"Topic text length: {len(topic_text)}")
    print(f"Topic text: {topic_text[:100]}...")
    translate_japanese_text(topic_text)
