# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : conjugation.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-10-31 14:21
# @UpdateTime : 2024-12-04 15:05

import random
import time
from collections import defaultdict

import requests
from pyquery import PyQuery as pq

# url = "https://www.babla.cn/%E5%8F%98%E4%BD%8D/%E5%BE%B7%E8%AF%AD/{word}"


def fetch_reverso_conjugation(word: str):
    time.sleep(random.randint(1, 3))
    reverso_base_url = (
        "https://conjugator.reverso.net/conjugation-german-verb-{word}.html"
    )
    url = reverso_base_url.format(word=word)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        print(
            f"Failed to fetch the page: {url}, reason: {response.reason}, text: {response.text}"
        )
        return False, None
    doc = pq(response.text)
    conj_block = doc("div.blue-box-wrap, div.blue-box-wrap.alt-tense")

    conj_result_list = []
    for conj in conj_block.items():
        conjugation = conj.attr("mobile-title")
        li_block = conj("li")
        if conjugation in [
            "Partizip Präsens",
            "Partizip Perfekt",
            "Infinitiv Präsens",
            "Infinitiv Perfekt",
            "Infinitiv zu + Infinitiv",
        ]:
            verb_list = []
            for li in li_block.items():
                verb = li.text().strip()
                verb_list.append(verb)
            conj_result_list.append([conjugation, "/".join(verb_list)])
        elif conjugation in ["Imperativ Präsens"]:
            verb_list = []
            for li in li_block.items():
                verb = li.text().strip()
                verb_list.append(verb)
            conj_result_list.append([conjugation, verb_list])
        else:
            verb_dict = defaultdict(list)
            for li in li_block.items():
                li_text = li.text()
                pronoun = li_text.split(" ")[0]
                verb = li_text.lstrip(pronoun).strip()
                if verb not in verb_dict[pronoun]:
                    verb_dict[pronoun].append(verb)
            verb_simplified = dict()
            for pronoun, verb_list in verb_dict.items():
                verb_simplified[pronoun] = "/".join(verb_list)
            conj_result_list.append([conjugation, verb_simplified])

    conj_result_dict = {}
    for conj_result in conj_result_list:
        conj_result_dict[conj_result[0]] = conj_result[1]
    return True, conj_result_dict


if __name__ == "__main__":
    word = "abfahren"

    print(fetch_reverso_conjugation(word))
