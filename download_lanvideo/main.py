import os
import sys
import urllib
from urllib import response
import requests
import wget
from urllib import parse
from pyquery import PyQuery as pq
import subprocess

url = "https://downloads-direct.freemdict.com/Language_Learning_Videos/Spanish"
root_dir = "/tmp/spanish/"


def progress_bar(current, total, width=50):
    progress = current / total
    bar = "#" * int(progress * width)
    percentage = round(progress * 100, 2)
    print(f"[{bar:<{width}}] {percentage}%")


def download(file_name, file_url):
    if file_name.endswith("/"):
        os.makedirs(file_name, exist_ok=True)
        response = requests.get(file_url)
        if response.status_code != 200:
            print(f"response.status_code: {response.status_code}")
        html = response.text
        with open("index.html", "w") as f:
            f.write(html)
        doc = pq(html)
        for a in doc("body > pre > a").items():
            sub_file = a.text().strip()
            sub_url = a.attr("href")
            # print(f"sub_file: {sub_file}, sub_url: {sub_url}")
            if sub_file.startswith(".."):
                continue
            if "01.西班牙语零基础语音入门" not in f"{file_name}{sub_file}":
                continue
            download(file_name + sub_file, file_url + sub_url)
    else:
        print(f"file_name: {file_name}, file_url: {file_url}")
        # wget.download(url=file_url, out=file_name, bar=progress_bar)
        # subprocess.call(["wget", "-c", file_url, "-O", file_name])


if __name__ == "__main__":
    new_url = f"{url}/02西语欧标/01.走遍西班牙(店家主推课程)等多个文件/"
    new_url_encode = parse.quote(new_url, safe=":/")
    download(root_dir, new_url_encode)
