# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : main
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-04-12 23:05
# @UpdateTime : TODO

import asyncio
import datetime
import html
import re
import subprocess
import traceback
from urllib.parse import urljoin, urlparse

import aiohttp
import lxml
import requests
from bs4 import BeautifulSoup
from lxml import etree as ET


async def request(url, headers, timeout=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            return await resp.text()


def get_level_class(num):
    return "level" + str(num)


def format_c_codes(code):

    with open("gitbook2md/input.txt", "w+", encoding="utf-8") as fp:
        fp.write(code)
    cmd = ["clang-format", "gitbook2md/input.txt"]
    try:
        out_bytes = subprocess.check_output(cmd)
        out_str = out_bytes.decode("utf-8")
        ret_code = 0
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        ret_code = e.returncode
    return out_str


class IndexParser:

    def __init__(self, lis, start_url):
        self.lis = lis
        self.start_url = start_url

    @classmethod
    def titleparse(cls, li):
        children = li.getchildren()
        if len(children) != 0:
            firstchildren = children[0]
            primeval_title = "".join(firstchildren.itertext())
            title = " ".join(primeval_title.split())
        else:
            title = li.text
        return title

    def parse(self):
        found_urls = []
        content_urls = []
        for li in self.lis:
            element_class = li.attrib.get("class")
            if not element_class:
                continue
            if "header" in element_class:
                title = self.titleparse(li)
                data_level = li.attrib.get("data-level")
                level = len(data_level.split(".")) if data_level else 1
                content_urls.append({"url": "", "level": level, "title": title})
            elif "chapter" in element_class:
                data_level = li.attrib.get("data-level")
                level = len(data_level.split("."))
                if "data-path" in li.attrib:
                    data_path = li.attrib.get("data-path")
                    url = urljoin(self.start_url, data_path)
                    title = self.titleparse(li)
                    if url not in found_urls:
                        content_urls.append(
                            {"url": url, "level": level, "title": title}
                        )
                        found_urls.append(url)

                # Unclickable link
                else:
                    title = self.titleparse(li)
                    content_urls.append({"url": "", "level": level, "title": title})
        return content_urls


class ChapterParser:
    def __init__(self, original, index_title, baselevel=0):
        self.heads = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
        self.original = original
        self.baselevel = baselevel
        self.index_title = index_title

    def parser(self):
        tree = ET.HTML(self.original)
        if tree.xpath('//section[@class="normal markdown-section"]'):
            context = tree.xpath('//section[@class="normal markdown-section"]')[0]
        else:
            context = tree.xpath('//section[@class="normal"]')[0]
        if context.find("footer"):
            context.remove(context.find("footer"))
        context = self.parsehead(context)
        return html.unescape(ET.tostring(context, encoding="utf-8").decode())

    def parsehead(self, context):
        def level(num):
            return "level" + str(num)

        for head in self.heads:
            if context.xpath(head):
                self.head = IndexParser.titleparse(context.xpath(head)[0])
                if self.head in self.index_title:
                    context.xpath(head)[0].text = self.index_title
                context.xpath(head)[0].attrib["class"] = level(self.baselevel)
                break
        return context


class Gitbook2PDF:
    def __init__(self, base_url, fname=None):
        self.fname = fname
        self.base_url = base_url
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }
        self.content_list = []
        self.meta_list = []
        self.meta_list.append(("generator", "gitbook2pdf"))

    def run(self):
        content_urls = self.collect_urls_and_metadata(self.base_url)
        self.content_list = ["" for _ in range(len(content_urls))]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl_main_content(content_urls))
        loop.close()

    async def crawl_main_content(self, content_urls):
        tasks = []
        for index, urlobj in enumerate(content_urls):
            if urlobj["url"]:
                tasks.append(
                    self.gettext(index, urlobj["url"], urlobj["level"], urlobj["title"])
                )
            else:
                tasks.append(self.getext_fake(index, urlobj["title"], urlobj["level"]))
        await asyncio.gather(*tasks)
        print("crawl : all done!")

    async def getext_fake(self, index, title, level):
        await asyncio.sleep(0.01)
        class_ = get_level_class(level)
        string = f"<h1 class='{class_}'>{title}</h1>"
        self.content_list[index] = string

    async def gettext(self, index, url, level, title):
        """
        return path's html
        """

        print("crawling : ", url)
        try:
            metatext = await request(url, self.headers, timeout=10)
        except Exception as e:
            print("retrying : ", url)
            metatext = await request(url, self.headers)
        try:
            text = ChapterParser(
                metatext,
                title,
                level,
            ).parser()
            print("done : ", url)
            self.content_list[index] = text
        except IndexError:
            print("faild at : ", url, " maybe content is empty?")

    def collect_urls_and_metadata(self, start_url):
        response = requests.get(start_url, headers=self.headers)
        self.base_url = response.url
        start_url = response.url
        text = response.text
        soup = BeautifulSoup(text, "html.parser")

        # If the output file name is not provided, grab the html title as the file name.
        if not self.fname:
            title_ele = soup.find("title")
            if title_ele:
                title = title_ele.text
                if "·" in title:
                    title = title.split("·")[1]
                if "|" in title:
                    title = title.split("|")[1]
                title = title.replace(" ", "").replace("/", "-")
                self.fname = title + ".pdf"
        self.meta_list.append(("title", self.fname.replace(".pdf", "")))

        # get description meta data
        comments_section = soup.find_all(class_="comments-section")
        if comments_section:
            description = comments_section[0].text.replace("\n", "").replace("\t", "")
            self.meta_list.append(("description", description))

        # get author meta
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta:
            author = author_meta.attrs["content"]
        else:
            author = urlparse(self.base_url).netloc
        self.meta_list.append(("author", author))

        # creation date and modification date : default now
        # see : https://www.w3.org/TR/NOTE-datetime
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        self.meta_list.append(("dcterms.created", now))
        self.meta_list.append(("dcterms.modified", now))
        lis = ET.HTML(text).xpath("//ul[@class='summary']//li")
        return IndexParser(lis, start_url).parse()


def task1(OUTPUT_PATH):
    # Linux C API 参考手册
    TASK_URL = "https://wizardforcel.gitbooks.io/linux-c-api-ref/"

    g = Gitbook2PDF(TASK_URL)
    g.run()

    info_list = []
    for content in g.content_list:
        try:
            updated_text = re.sub(r"<(([a-z]+/)*[a-z]+\.h)>", r"{{{\1}}}", content)
            root = ET.HTML(updated_text)
        except Exception:
            print("error", content)
            continue
        cat_flag = False
        for child in root.iter():
            if child.tag == "h1":
                info_list.append("## {}".format(child.text.strip()))
            elif child.tag == "h2":
                info_list.append("### {}\n".format(child.text.strip()))
                print(child.text)
            elif child.tag == "h3":
                info_list.append("**{}**: ".format(child.text.strip()))
                if child.attrib["id"] != "范例" and child.attrib["id"] != "执行":
                    cat_flag = True
            elif child.tag == "p" and child.text:
                if cat_flag:
                    cat_flag = False
                    info_list[-1] = info_list[-1] + child.text.strip()
                else:
                    info_list.append(child.text.strip())
            elif child.tag == "code" and child.text:
                updated_text = re.sub(r"{{{(.*?)}}}", r"<\1>", child.text.strip())
                if cat_flag:
                    cat_flag = False
                    info_list[-1] = info_list[-1] + "`{}`".format(
                        updated_text.replace("\n", ", ")
                    )
                else:
                    info_list.append("```c\n{}\n```".format(updated_text))
            elif (
                child.tag == "pre" or child.tag == "html" or child.tag == "body"
            ) and not child.text:
                continue
            elif child.tag == "section":
                continue
            else:
                print(child.tag, child.attrib, child.text)
        info_list.append("")

    with open(OUTPUT_PATH, "w+", encoding="utf-8") as fp:
        fp.write("\n".join(info_list))


if __name__ == "__main__":

    task1(OUTPUT_PATH="gitbook2md/output.md")

    # code = open('gitbook2md/input.txt', encoding='utf-8').read()
    # cmd = ["clang-format", "gitbook2md/input.txt"]
    # try:
    #     out_bytes = subprocess.check_output(cmd)
    #     out_str = out_bytes.decode('utf-8')
    #     ret_code = 0
    # except subprocess.CalledProcessError as e:
    #     out_bytes = e.output
    #     ret_code = e.returncode

    # print(out_str)

    # origin_text = open('gitbook2md/input.txt', encoding='utf-8').read()
    # updated_text = re.sub(r"<([a-z]+\.h)>", r"{{{\1}}}", origin_text)
    # print(updated_text)
    # lxml.html.fromstring(updated_text)
    # root = ET.HTML(origin_text)
    # for child in root.iter():
    #     print(child.tag, child.attrib, child.text)

    # soup = BeautifulSoup(updated_text, features="lxml")
    # print(soup.prettify())
