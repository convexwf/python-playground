# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : subtitle-parse/srt_parse.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import pysrt
import re
import os
import chardet
import pysubs2


def clean_text(text):
    cleaned_text = re.sub(r"\{.*?\}", "", text)
    cleaned_text = cleaned_text.replace("\\n", " ")
    params = cleaned_text.split("\n")
    if len(params) == 2:
        cleaned_text = f"{params[1]} / {params[0]}"
    return cleaned_text.strip()


def extract_ass(filename):
    encoding = chardet.detect(open(filename, "rb").read())["encoding"]
    print(f"Detected encoding: {encoding} for {filename}")
    subs = pysubs2.load(filename, encoding=encoding)
    subtitle_list = []
    for event in subs.events:
        text = event.text
        text_no_styles = re.sub(r"\{.*?\}", "", text)
        text_no_styles = text_no_styles.replace("\\n", " ")
        parts = re.split(r"\\N", text_no_styles)

        if len(parts) != 2:
            # print(f"Error for text: {text_no_styles}")
            subtitle_list.append(text_no_styles)
            continue

        chinese_part = parts[0].strip()
        english_part = parts[1].strip()
        subtitle_list.append(f"{english_part} / {chinese_part}")
    return subtitle_list


def extract_srt(filename):
    encoding = chardet.detect(open(filename, "rb").read())["encoding"]
    try:
        subs = pysrt.open(filename, encoding=encoding)
        # print(f"Detected encoding: {encoding} for {filename}")
        subtitle_list = []
        for sub in subs:
            text = clean_text(sub.text)
            subtitle_list.append(text)
        return subtitle_list
    except Exception as e:
        print(f"****Error: {e} for {filename}")
    return []


if __name__ == "__main__":
    # subs = pysrt.open("test.srt", encoding="GB2312")

    season = "S01"
    root_dir = f"C:/Users/convexwf/Downloads/半沢直樹/{season}"

    info_list = [f"# 半沢直樹 {season}\n"]
    for episodde_idx, episode in enumerate(sorted(os.listdir(root_dir))):
        filepath = f"{root_dir}/{episode}"
        if filepath.endswith(".srt"):
            subtitle_list = extract_srt(filepath)
        elif filepath.endswith(".ass"):
            subtitle_list = extract_ass(filepath)
        info_list.append(f"\n## {season}E{episodde_idx+1:02d}\n\n")
        for text in subtitle_list:
            if len(text) == 0:
                continue
            if text.startswith("-") or text.startswith("*"):
                text = f"\\{text}"
            info_list.append(f"{text}  \n")
    with open(f"{season}.md", "w+", encoding="utf-8") as f:
        f.writelines(info_list)
