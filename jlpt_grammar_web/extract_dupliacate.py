# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : extract_dupliacate.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-09-10 11:35
# @UpdateTime : TODO

import os


def filter_by_prefix(word_dict, prefix):
    # return [word for word in word_list if word.startswith(prefix)]
    word_list = []
    for word, visited in word_dict.items():
        if word.startswith(prefix) and not visited:
            word_dict[word] = True
            word_list.append(word)
    return word_list


def filter_by_suffix(word_dict, suffix):
    word_list = []
    for word, visited in word_dict.items():
        if word.endswith(suffix) and not visited:
            word_dict[word] = True
            word_list.append(word)
    return word_list


def extract_fuhedongci(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    title_list = []
    word_dict = {}
    for line in lines:
        if line.strip() == "":
            continue
        if line.startswith("###"):
            title_list.append(line.strip()[4:])
        else:
            word_dict[line.strip()] = False

    def custom_sort(s):
        return (0 if s.startswith("～") else 1, s)

    title_list = sorted(title_list, key=custom_sort)

    title_dict = {}
    for title in title_list:
        title_dict[title] = []
        subtitle_list = title.split("/")
        for subtitle in subtitle_list:
            if subtitle.startswith("～"):
                title_dict[title].extend(filter_by_suffix(word_dict, subtitle[1:]))
            elif subtitle.endswith("～"):
                title_dict[title].extend(filter_by_prefix(word_dict, subtitle[:-1]))
            # else:
            #     title_dict["（その他）"].append(subtitle)

    for word, visited in word_dict.items():
        if not visited:
            title_dict["（その他）"].append(word)

    return title_dict


if __name__ == "__main__":
    input_file = "tmp/output_复合动词.md"
    title_dict = extract_fuhedongci(input_file)

    with open("tmp/output_复合动词.md", "w+", encoding="utf-8") as f:
        for title, word_list in title_dict.items():
            f.write("### " + title + "\n\n")
            for word in word_list:
                f.write(word + "\n")
            f.write("\n")
