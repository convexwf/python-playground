# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : pyOpenCV-exp
# @FileName : size.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-02-11 12:42
# @UpdateTime : Todo

import cv2

img_path = "pyOpenCV-exp/res/vx.png"
out_path = "pyOpenCV-exp/res/output.png"


def convert1():
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    h, w, d = img.shape

    rows = [
        22,
        40,
        40,
        22,
        22,
        22,
        16,
        16,
        0,
        0,
        40,
        22,
        22,
        16,
    ]
    res = []
    for i, row in enumerate(rows):
        part_img = img[row:-1, i * 60 : (i + 1) * 60, :]
        res.append(cv2.resize(part_img, dsize=(60, 60)))
    cv2.imwrite(out_path, cv2.hconcat(res))


if __name__ == "__main__":
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    print(img.shape)
    h, w, d = img.shape
    res = []
    for i in range(3):
        for j in range(4):
            res.append(
                cv2.resize(
                    img[j * 32 : (j + 1) * 32, i * 32 : (i + 1) * 32, :], dsize=(60, 60)
                )
            )
    cv2.imwrite(out_path, cv2.hconcat(res))
