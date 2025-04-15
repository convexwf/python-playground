# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : openai_test/main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if __name__ == "__main__":
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://chat.cloudapi.vip/v1/",
    )

    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a coding assistant that talks like a pirate.",
        input="How do I check if a Python object is an instance of a class?",
    )

    print(response.output_text)
