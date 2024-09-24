# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : N1
# @FileName : extract_grammar.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-07-08 20:04
# @UpdateTime : TODO

import os
import random
import time

import requests
from pyquery import PyQuery as pq

url = "https://mainichi-nonbiri.com/grammar/n1-atteno/"


def get_summary():
    g_url = "https://mainichi-nonbiri.com/japanese-grammar/"
    html = requests.get(g_url)
    doc = pq(html.text)
    content = doc('div[class="post_content"]')

    flag = False
    content_list = ["# レベル順"]
    for child in content.children():
        if child.tag == "h2":
            if child.text.strip() == "レベル順":
                flag = True
            else:
                flag = False
        if not flag:
            continue
        if child.tag == "h3":
            content_list.append(f"\n## {child.text}\n")
        else:
            a_list = pq(pq(child).outer_html())("a")
            links = [a.attr["href"] for a in a_list.items()]
            content_list.append("\n".join(links))

    with open("n1_grammar_summary.md", "w+", encoding="utf-8") as f:
        f.write("\n".join(content_list))


def list_summary():
    url_list = []
    with open("n1_grammar_summary.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if not line.startswith("http"):
                continue
            url = line.strip()
            url_list.append(url)
    return url_list


def merge_unit():
    content_list = []
    with open("n1_grammar_summary.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[2:]:
            if not line.startswith("http"):
                if line.startswith("##"):
                    line = line.replace("##", "#")
                content_list.append(line)
                continue
            filename = line.strip().split("/")[-2]
            with open(f"grammar/{filename}.md", "r", encoding="utf-8") as f:
                content_list.append("\n#" + f.read() + "\n")
            # break
    with open("n1_grammar.md", "w+", encoding="utf-8") as f:
        f.write("".join(content_list))


def unit(url):
    filename = url.split("/")[-2]
    if os.path.exists(f"grammar/{filename}.md"):
        return
    os.makedirs("grammar", exist_ok=True)

    html = requests.get(url)
    doc = pq(html.text)
    h1 = doc("h1").text()

    content_list = [f"# {h1}"]
    content = doc('div[class="post_content"]')
    for child in content.children():
        if child.tag == "h3":
            # print(child.text)
            content_list.append(f"\n**{child.text}**\n")
            content_list.append("")
        else:
            full_text = pq(child).outer_html()
            text = (
                pq(full_text).text().strip().replace("\u3000", "").replace("\n", "\n\n")
            )
            content_list[-1] += text
    # print(content_list)

    with open("grammar/" + filename + ".md", "w+", encoding="utf-8") as f:
        f.write("\n".join(content_list) + "\n")
    with open("grammar/mapping.md", "a+", encoding="utf-8") as f:
        f.write(f"{filename}\t{h1}\n")


if __name__ == "__main__":
    # unit(url)
    # url_list = list_summary()
    # for url in url_list:
    #     unit(url)
    #     print(f"Finished {url}")
    #     time.sleep(random.randint(1, 3))

    merge_unit()
