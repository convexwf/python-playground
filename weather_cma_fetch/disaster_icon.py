# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : disaster_icon.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-10-12 17:16
# @UpdateTime : TODO

import os
import re

import requests
from PIL import Image

BASE_URL = "https://weather.cma.cn/"
output_dir = "resources"
# https://weather.cma.cn/assets/img/alarm/p0002003.png


def combine_images(image_paths, output_path, rows, cols):
    """
    合并多张图片为指定行列的网格，并保存到指定路径。

    :param image_paths: List[str] - 输入图片的文件路径列表
    :param output_path: str - 输出合并后图片的文件路径
    :param rows: int - 行数
    :param cols: int - 列数
    """

    # 确保图片数量能填满行列
    if len(image_paths) != rows * cols:
        raise ValueError("输入的图片数量必须等于 rows * cols")

    # 加载图片
    images = [Image.open(image_path) for image_path in image_paths]

    # 获取每张图片的宽度和高度
    width = max(image.width for image in images) + 5
    height = max(image.height for image in images) + 5
    total_width = width * cols
    total_height = height * rows

    # 创建一个新图像，用于合并
    new_image = Image.new("RGB", (total_width, total_height))

    # 将图片粘贴到新图像上
    for index, image in enumerate(images):
        x_offset = (index % cols) * width
        y_offset = (index // cols) * height
        new_image.paste(image, (x_offset, y_offset))

    # 保存合并后的图片
    new_image.save(output_path)
    print(f"合并后的图片已保存为: {output_path}")


def fetch_icon_file(icon_code: str):
    url = f"{BASE_URL}assets/img/alarm/{icon_code}.png"
    output_icon_dir = os.path.join(output_dir, "icon")
    os.makedirs(output_icon_dir, exist_ok=True)

    # Download the icon file
    response = requests.get(url)
    if response.status_code != 200:
        return False
    with open(f"{output_icon_dir}/{icon_code}.png", "wb") as f:
        f.write(response.content)
    return True


if __name__ == "__main__":
    # stop_flag = False
    # for disaster_code in range(1, 45):
    #     for disaster_level in range(5, 6):
    #         icon_code = f"p{str(disaster_code).zfill(4)}{str(disaster_level).zfill(3)}"
    #         print(
    #             f"Fetching icon {icon_code} code: {disaster_code} level: {disaster_level}"
    #         )
    #         if not fetch_icon_file(icon_code):
    #             print(f"Failed to fetch icon {icon_code}")
    #             # stop_flag = True
    #             # break
    #     if stop_flag:
    #         break

    image_path_list = []
    for disaster_code in range(1, 45):
        disaster_level = 1
        pcode = f"p{str(disaster_code).zfill(4)}{str(disaster_level).zfill(3)}"
        image_path_list.append(f"{output_dir}/icon/{pcode}.png")
    combine_images(image_path_list, f"{output_dir}/disaster_icons.png", 4, 11)
