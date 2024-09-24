# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : jlpt-review
# @FileName : kannyouu_trans.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-09-07 21:16
# @UpdateTime : TODO

import json
from collections import defaultdict

import pykakasi
import pyquery as pq
import requests

kks = pykakasi.kakasi()

request_url = "https://proverb-encyclopedia.com/{romaji}/"


def convert_romaji(text):
    result = kks.convert(text)
    return "".join([item["hepburn"] for item in result])


def get_translations(input_text):
    romaji = convert_romaji(input_text)
    url = request_url.format(romaji=romaji)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to request {input_text}({romaji}). url: {url}")
        return {}
    doc = pq.PyQuery(response.text)
    entry = doc("section[class='entry-content cf']")

    result_dict = dict()
    result_dict["url"] = url
    result_dict["【慣用句】"] = input_text

    for p in entry.children():
        if p.tag == "p":
            text = pq.PyQuery(p).text().replace("\n", "")
            if text.startswith("【読み方】"):
                result_dict["【読み方】"] = text[5:]
            elif text.startswith("【意味】"):
                result_dict["【意味】"] = text[4:]
            elif text.startswith("【語源由来】"):
                result_dict["【語源由来】"] = text[6:]

    result_dict["【例文】"] = []
    for sentence in entry("ol > li").items():
        result_dict["【例文】"].append(sentence.text())

    meaning = entry("div[class='cboxcomment']")
    if meaning:
        result_dict["【解説】"] = meaning.text()

    return result_dict


def output_markdown(result_dict):
    info_list = []
    info_list.append(f"**【慣用句】** {result_dict['【慣用句】']}\n")
    info_list.append(f"**【読み方】** {result_dict['【読み方】']}\n")
    info_list.append(f"**【意味】** {result_dict['【意味】']}\n")
    info_list.append(f"**【意味(中文)】** {result_dict['【意味(中文)】']}\n")
    if "【語源由来】" in result_dict:
        info_list.append(f"**【語源由来】** {result_dict['【語源由来】']}\n")
    if "【解説】" in result_dict:
        detail_text = "> " + result_dict["【解説】"].replace("\n", "\n> ")
        info_list.append(f"**【解説】**\n\n{detail_text.strip()}\n\n")
    info_list.append("**【例文】**\n\n```janpanese\n")
    for sentence in result_dict["【例文】"]:
        info_list.append(sentence + "\n")
    info_list.append("```\n")
    return info_list


def get_kannyou_list():
    with open("tmp/kannyou_list.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 虫が好かない「むしをすかない」：讨厌
    kannyou_list = []
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            category = line.split(" ")[1]
            continue
        kannyou = line.split("「")[0].strip()
        spell = line.split("「")[1].split("」")[0].strip()
        meaning = line.split("：")[1].strip()
        # print(f"kannyou: {kannyou}, spell: {spell}, meaning: {meaning}")
        kannyou_list.append((category, kannyou, spell, meaning))
    return kannyou_list


if __name__ == "__main__":
    # input_text = "気が早い"
    # translations = get_translations(input_text)
    # info_list = output_markdown(translations)
    # with open("result.md", "w", encoding="utf-8") as f:
    #     f.writelines(info_list)
    # print(translations)

    info_list = []
    proverb_dict = {}
    kannyou_list = get_kannyou_list()
    current_category = ""
    for kannyou in kannyou_list:
        category, kannyou, spell, meaning = kannyou
        # print(
        #     f"category: {category}, kannyou: {kannyou}, spell: {spell}, meaning: {meaning}"
        # )

        if category != current_category:
            info_list.append(f"## {category}\n\n")
            current_category = category
        translations = get_translations(kannyou)
        if translations:
            info_list.append(f"### {kannyou}\n\n")
            translations["【意味(中文)】"] = meaning
            proverb_dict[translations["【慣用句】"]] = translations
            kannyou_info = output_markdown(translations)
            info_list.extend(kannyou_info)
            info_list.append("\n")
        else:
            info_list.append(f"### X{kannyou}\n\n")
            info_list.append(f"**【慣用句】** {kannyou}\n")
            info_list.append(f"**【読み方】** {spell}\n")
            info_list.append(f"**【意味(中文)】** {meaning}\n\n")

    with open("tmp/kannyou_output.md", "w", encoding="utf-8") as f:
        f.writelines(info_list)

    with open("tmp/kannyou_dict.json", "w", encoding="utf-8") as f:
        json.dump(proverb_dict, f, ensure_ascii=False, indent=2)
