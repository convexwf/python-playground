# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-01-14 12:14
# @UpdateTime : 2025-01-14 12:14

import requests
from dotenv import load_dotenv
import os
from pyquery import PyQuery as pq
import datetime
import time
import random

load_dotenv()


def convert_date_chinese_to_format(date_str):
    """
    Converts a Chinese date string to a datetime object.

    Args:
        date_str (str): The date string in Chinese format (e.g., "2025年7月10日").

    Returns:
        datetime.datetime: The corresponding datetime object.
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y年%m月%d日")
    except ValueError as e:
        raise ValueError(f"Date format error: {e}")


def douban_group_topic_crawler():
    """
    Crawls 【天声人語】 topic from Douban group.
    """
    start = 0
    url = f"https://www.douban.com/group/612024/discussion?start={start}&type=new"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    cookie_str = os.getenv("DOUBAN_COOKIE")
    cookies = dict(item.split("=", 1) for item in cookie_str.split("; "))

    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve the page, status code: {response.status_code} {response.text}"
        )
    html_content = response.text
    doc = pq(html_content)
    link_list = list(doc("td[class='title'] > a").items())

    def get_topic_text(url, headers, cookies):
        """
        Fetches the douband topic text from the given URL.

        Args:
            url (str): The URL of the Douban topic.
            headers (dict): HTTP headers to use for the request.
            cookies (dict): Cookies to use for the request.

        Returns:
            str: The text content of the topic.
        """
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve the page, status code: {response.status_code}"
            )
        html_content = response.text
        doc = pq(html_content)
        doc("script").remove()  # Remove script tags
        topic_block = doc("div#link-report")
        topic_text = topic_block.text().strip()
        # Replace single newlines with double newlines for better readability
        topic_text = topic_text.replace("\n", "\n\n")

        return topic_text

    for idx, link in enumerate(link_list):
        if idx >= 3:
            break
        topic_url = link.attr("href")
        topic_title: str = link.attr("title")
        print(f"Processing topic: {topic_title} - {topic_url}")

        caption, chinese_date_str = topic_title.rsplit(" ", 1)
        if not caption.startswith("【天声人語】"):
            continue
        topic_caption = caption[len("【天声人語】") :].strip()
        topic_date = convert_date_chinese_to_format(chinese_date_str)

        try:
            time.sleep(random.uniform(1, 3))  # Random sleep to avoid rate limiting
            topic_text = get_topic_text(topic_url, headers, cookies)
            with open("tmp/douban_topic.txt", "a+", encoding="utf-8") as f:
                f.write(f"### {topic_date.strftime('%Y-%m-%d')}\n\n")
                f.write(f"**{topic_caption}**\n\n")
                f.write(topic_text + "\n\n")
        except Exception as e:
            print(f"Error fetching topic text: {e}")


if __name__ == "__main__":
    douban_group_topic_crawler()
