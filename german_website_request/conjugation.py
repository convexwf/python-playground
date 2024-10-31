# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : conjugation.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-10-31 14:21
# @UpdateTime : 2024-10-31 14:21

from collections import defaultdict

import requests
from pyquery import PyQuery as pq

# url = "https://www.babla.cn/%E5%8F%98%E4%BD%8D/%E5%BE%B7%E8%AF%AD/{word}"


def fetch_reverse_conjugation(word: str):
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
    conj_block = doc("div[class='blue-box-wrap']")

    conj_result = []
    for conj in conj_block.items():
        conjugation = conj.attr("mobile-title")
        li_block = conj("li")
        if conjugation not in ["Partizip Präsens", "Partizip Perfekt"]:
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
            conj_result.append([conjugation, verb_simplified])
        else:
            verb = li_block.text().strip()
            conj_result.append([conjugation, verb])
    return True, conj_result


if __name__ == "__main__":
    word = "lesen"

    print(fetch_reverse_conjugation(word))
