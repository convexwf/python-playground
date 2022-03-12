# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : utils
# @FileName : utils.py
# @Author : convexwf@gmail.com
# @CreateDate : 2022-02-25 21:00
# @UpdateTime : Todo

import copy
import random
import numpy as np
import cv2

def read_csv(csv_name):
    res = np.zeros(shape=(14, 14), dtype=np.float)
    with open(csv_name, encoding='utf-8') as fp:
        lines = fp.readlines()
        for i in range(14):
            params = lines[i+1].strip().split(',')
            for j in range(14):
                if len(params[j+1]) > 0:
                    res[i, j] = float(params[j+1])
                    res[j, i] = float(params[j+1])
    return res


def read_unit(csv_name):
    gates = []  # 6*2
    units = []
    with open(csv_name, encoding='utf-8') as fp:
        lines = fp.readlines()
        for line in lines[0:8]:
            units.append([float(it) for it in line.strip().split(',')])
        for line in lines[8:14]:
            gates.append([float(line.strip().split(',')[1]),
                         float(line.strip().split(',')[2])])
        paint = [float(lines[14].strip().split(',')[1]),
                 float(lines[14].strip().split(',')[2])]
        for line in lines[15:]:
            units.append([float(it) for it in line.strip().split(',')])
    return units, gates, paint


def post_process(units):
    units_ids = [int(it[0]) for it in units]
    units_map = {int(it[0]): (it[1], it[2]) for it in units}
    return units_ids, units_map


def split_area(L, C_x1, C_x2, c, delta_d, delta_l):
    L_areas = []
    for i in range(4):
        L_areas.append(C_x1-c/2-delta_l-delta_d)
        L_areas.append(C_x2-C_x1-c-2*delta_d)
        L_areas.append(L-C_x2-c/2-delta_l-delta_d)
    return L_areas[:-1]

def split_Larea(L, C_x1, C_x2, c, delta_d, delta_l):
    column = []
    length = []
    for i in range(4):
        column.append(L*i+delta_l)
        column.append(L*i+C_x1+c/2+delta_d)
        column.append(L*i+C_x2+c/2+delta_d)
        length.append(C_x1-c/2-delta_l-delta_d)
        length.append(C_x2-C_x1-c-2*delta_d)
        length.append(L-C_x2-c/2-delta_l-delta_d)
    return column[:-1], length[:-1]

def recombinate(src, _in, _out):
    dst = copy.deepcopy(src)
    for i, j in zip(_in, _out):
        dst[j] = src[i]
    return dst


def addpoint(src, pivot, add_value):
    dst = copy.deepcopy(src)
    dst[pivot] += add_value * 0.1
    if dst[pivot] < 0.:
        dst[pivot] = 0.
    return dst


def swap_point(Alist, Blist, pivots):
    Ares, Bres = copy.deepcopy(Alist), copy.deepcopy(Blist)
    for pivot in pivots:
        Ares[pivot] = Blist[pivot]
        Bres[pivot] = Alist[pivot]
    return Ares, Bres

def instead(src, x_pivots, _in, _out):
    _in = copy.deepcopy(_in)
    idx = 0
    for i in range(len(src)):
        if i not in x_pivots and src[i] in _in:
            _in.remove(src[i])
            src[i] = _out[idx]
            idx += 1

# 轮盘赌
def roulette(select_list):
    sum_val = sum(select_list)
    random_val = random.random()
    probability = 0
    for i in range(len(select_list)):
        probability += select_list[i] / sum_val
        if probability >= random_val:
            return i
        else:
            continue

def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=20):
    dist = ((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts = []
    for i in np.arange(0, dist, gap):
        r = i/dist
        x = int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y = int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x, y)
        pts.append(p)
    if style == 'dotted':
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i % 2 == 1:
                cv2.line(img, s, e, color, thickness)
            i += 1

def put_text(img, uid, x, y, l, w):
    # rows, cols, depth = img.shape
    xc, yc = int(100 + 10 * x), int(100 + 10 * y)
    x1, x2 = int(100 + 10 * (x - l/2)), int(100 + 10 * (x + l/2))
    y1, y2 = int(100 + 10 * (y - w/2)), int(100 + 10 * (y + w/2))
    cv2.rectangle(img, (x1, y1), (x2, y2), color=(255, 0, 0, 120), thickness=1, lineType=cv2.LINE_8)
    cv2.circle(img, (xc, yc), radius=2, color=(0, 0, 0, 255), thickness=-1)
    cv2.putText(img, str(uid), (x1, y2-15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0, 255), 2, bottomLeftOrigin=True)
    cv2.putText(img, str(l), (xc-5, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (205, 0, 0, 255), 1, bottomLeftOrigin=True)
    cv2.putText(img, str(w), (x1, yc), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (205, 0, 0, 255), 1, bottomLeftOrigin=True)
    cv2.putText(img, '({:.1f},{:.1f})'.format(x, y), (xc, yc), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 205, 255), 1, bottomLeftOrigin=True)