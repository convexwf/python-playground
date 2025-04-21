# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : jlpt_grammar_web/jlpt_test_data.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-21 13:19
# @UpdateTime : 2025-04-21 13:19

import re

import requests
from pyquery import PyQuery as pq

# https://www.dethitiengnhat.com/en/jlpt/N1/201012/1

BASE_URL = "https://www.dethitiengnhat.com/en/jlpt/{level}/{year_month}/{part}"


def extract_jlpt_N1_vocab_1to3(year_month_list):

    info_list = "# JLPT N1 Vocabulary (Type 1-3)\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="1")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Vocabulary (Type 1-3) ...")

        result = [[] for _ in range(19)]
        question_block = doc("div[class='question_list']")
        for number, question in enumerate(list(question_block.items())[0:19]):
            u_tag = question("u")
            u_text = ""
            if u_tag:
                u_text = u_tag.text().strip()
            question_text = question.text().strip()
            pivot = 1 if number < 9 else 2
            question_no = question_text[0:pivot]
            question_text = (
                "**【" + question_no + "】** " + question_text[pivot + 1 :].strip()
            )
            question_text = question_text.replace(f"\n{u_text}\n", f"<u>{u_text}</u>")
            result[number].append(question_text)

        answer_block = doc("div[class='answers']")
        four_answers = list(answer_block.items())[0 : 19 * 4]
        for number in range(19):
            answer_text = ">"
            for answer in four_answers[number * 4 : number * 4 + 4]:
                choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text().strip())
                answer_text += " " + choice_text
            result[number].append(answer_text)

        info_list += f"## {year_month}\n\n"
        for question, answer in result:
            info_list += f"{question}\n\n{answer}\n\n"

    with open("jlpt_N1_vocab_type1to3.md", "w+", encoding="utf-8", newline="\n") as f:
        f.writelines(info_list)


def extract_jlpt_N1_vocab_type4(year_month_list):

    info_list = "# JLPT N1 Vocabulary (Type 4)\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="2")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Vocabulary (Type 4) ...")

        result = [[] for _ in range(6)]
        question_block = doc("div[class='question_list']")
        for number, question in enumerate(list(question_block.items())[19 : 19 + 6]):
            question_text = question.text().strip()
            question_no = question_text[0:2]
            question_text = "**【" + question_no + "】** " + question_text[3:].strip()
            result[number].append(question_text)

        answer_block = doc("div[class='answers']")
        four_answers = list(answer_block.items())[76 : 76 + 6 * 4]
        for number in range(6):
            answer_text = ""
            for answer in four_answers[number * 4 : number * 4 + 4]:
                choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text().strip())
                u_tag = answer("u")
                u_text = ""
                if u_tag:
                    u_text = u_tag.text().strip()
                answer_text += (
                    "> "
                    + choice_text.replace(f"\n{u_text}\n", f"<u>{u_text}</u>")
                    + "\n"
                )
            result[number].append(answer_text)

        info_list += f"## {year_month}\n\n"
        for question, answer in result:
            info_list += f"{question}\n\n{answer}\n"

    with open("jlpt_N1_vocab_type4.md", "w+", encoding="utf-8", newline="\n") as f:
        f.writelines(info_list)


def extract_jlpt_N1_grammar_type4(year_month_list):

    info_list = "# JLPT N1 Grammar (Type 4)\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="1")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Grammar (Type 4) ...")

        result = [[] for _ in range(10)]
        question_block = doc("div[class='question_list']")
        for number, question in enumerate(list(question_block.items())[25 : 25 + 10]):
            question_text = question.text().strip()
            question_no = question_text[0:2]
            question_text = "**【" + question_no + "】** " + question_text[3:].strip()
            result[number].append(question_text)

        answer_block = doc("div[class='answers']")
        four_answers = list(answer_block.items())[100 : 100 + 10 * 4]
        for number in range(10):
            answer_text = ">"
            for answer in four_answers[number * 4 : number * 4 + 4]:
                choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text().strip())
                answer_text += " " + choice_text
            result[number].append(answer_text)

        info_list += f"## {year_month}\n\n"
        for question, answer in result:
            info_list += f"{question}\n\n{answer}\n\n"

    with open("jlpt_N1_grammar_type4.md", "w+", encoding="utf-8", newline="\n") as f:
        f.writelines(info_list)


def extract_jlpt_N1_grammar_type5(year_month_list):

    info_list = "# JLPT N1 Grammar (Type 5)\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="2")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Grammar (Type 5) ...")

        result = [[] for _ in range(5)]
        question_block = doc("div[class='question_list']")
        for number, question in enumerate(list(question_block.items())[35 : 35 + 5]):
            question_text = question.text().strip()
            question_no = question_text[0:2]
            question_text = "**【" + question_no + "】** " + question_text[3:].strip()
            result[number].append(question_text)

        answer_block = doc("div[class='answers']")
        four_answers = list(answer_block.items())[140 : 140 + 5 * 4]
        for number in range(5):
            answer_text = ">"
            for answer in four_answers[number * 4 : number * 4 + 4]:
                choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text().strip())
                answer_text += " " + choice_text
            result[number].append(answer_text)

        info_list += f"## {year_month}\n\n"
        for question, answer in result:
            info_list += f"{question}\n\n{answer}\n\n"

    with open("jlpt_N1_grammar_type5.md", "w+", encoding="utf-8", newline="\n") as f:
        f.writelines(info_list)


def extract_jlpt_N1_grammar_type6(year_month_list):

    info_list = "# JLPT N1 Grammar (Type 6)\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="1")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Grammar (Type 6) ...")

        question_block = doc("div[class='question_content']")
        if not question_block:
            continue
        question_text = question_block.text().strip()
        info_list += f"## {year_month}\n\n"
        info_list += f"{question_text}\n\n"

        answer_block = doc("div[class='answers']")
        four_answers = list(answer_block.items())[160 : 160 + 4 * 5]
        for number in range(5):
            answer_text = f"**【{40 + number + 1}】**\n"
            for answer in four_answers[number * 4 : number * 4 + 4]:
                choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text().strip())
                answer_text += "> " + choice_text + "\n"
            info_list += f"{answer_text}\n"

    with open("jlpt_N1_grammar_type6.md", "w+", encoding="utf-8", newline="\n") as f:
        f.writelines(info_list)


def extract_jlpt_N1_listening(year_month_list):
    info_list = "# JLPT N1 Listening\n\n"

    for year_month in year_month_list:
        url = BASE_URL.format(level="N1", year_month=year_month, part="4")
        response = requests.get(url)
        if response.status_code != 200 or "問題" not in response.text:
            continue
        doc = pq(response.text)

        print(f"Extracting {year_month} N1 Listening ...")

        info_list = [f"# {year_month} N1 听力原文\n\n"]
        big_index = 0
        GT_index = 1
        form = doc("form[name='dttn']")
        for div_child in form.children():
            if div_child.tag != "div":
                continue
            if div_child.attrib.get("class") == "big_item":
                big_index += 1
                info_list.append(f"## 問題{big_index}\n\n")
            elif div_child.attrib.get("class") == "question_list":
                bango = div_child.text.strip()
                info_list.append(f"**{bango}**\n\n")
            elif div_child.attrib.get("id") == f"GT{GT_index}":
                GT_index += 1
                refer = (
                    pq(div_child)
                    .text()
                    .strip()
                    .replace("\n\n", "\n")
                    .replace("\n", "  \n")
                )
                if refer.startswith("Reference: "):
                    refer = refer[11:]
                info_list.append(f"{refer}\n\n")
            else:
                answers = pq(div_child)("label > div")
                if not answers:
                    continue
                if big_index == 3 or big_index == 4:
                    continue
                for answer in answers:
                    choice_text = re.sub(r"\d\)", "`\g<0>`", answer.text.strip())
                    info_list.append(f"> {choice_text}\n")
                info_list.append("\n")
        with open(f"tmp/{year_month}.md", "w+", encoding="utf-8", newline="\n") as f:
            f.writelines(info_list)


if __name__ == "__main__":
    year_month_list = []
    for year in range(2010, 2025):
        for month in ["07", "12"]:
            year_month = str(year) + month
            year_month_list.append(year_month)

    # extract_jlpt_N1_vocab_1to3(year_month_list)
    # extract_jlpt_N1_vocab_type4(year_month_list)
    # extract_jlpt_N1_grammar_type4(year_month_list)
    # extract_jlpt_N1_grammar_type5(year_month_list)
    # extract_jlpt_N1_grammar_type6(year_month_list)

    extract_jlpt_N1_listening(year_month_list)
