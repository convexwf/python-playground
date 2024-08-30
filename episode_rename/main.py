# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : episode_rename
# @FileName : main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-08-30 20:49
# @UpdateTime : TODO

import os
import re

def is_valid_filename(filename):  
    # 定义非法字符，包括制表符  
    illegal_chars = r'[<>:"/\\|?*\t]'  
    # 定义保留文件名  
    reserved_names = {  
        "CON", "PRN", "AUX", "NUL",  
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",  
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"  
    }  
    
    # 检查文件名长度  
    if len(filename) > 255:  
        return False  
    
    # 检查非法字符  
    if re.search(illegal_chars, filename):
        return False  
    
    # 检查保留文件名  
    if filename.upper() in reserved_names:  
        return False  
    
    # 检查文件名是否以空格或句点结尾  
    if filename.endswith(' ') or filename.endswith('.'):  
        return False  
    
    # 检查文件名是否包含控制字符（ASCII 0-31）  
    if any(ord(char) < 32 for char in filename):  
        return False  
    
    return True  

def rename_tv_series(config):
    # https://next-episode.net/
    with open(f"TV_series/{config}.txt", "r") as f:
        lines = f.readlines()
    
    name_list = []
    for line in lines[1:]:
        if not line[0].isdigit():
            name_list.append([line.strip()])
        else:
            episode = line.split("\t")[1]
            name_list[-1].append(episode.strip())

    video_dir = lines[0].strip()
    for season in name_list:
        season_name = season[0]
        src_episode_list = sorted(os.listdir(f"{video_dir}/{season_name}"))
        if len(season[1:]) != len(src_episode_list):
            print(f"{config} Season {season_name} episode number mismatch")
            continue
        count = 1
        for src, dst in zip(src_episode_list, season[1:]):
            suffix = src.split(".")[-1]
            dst = f"{season_name}E{count:02d}.{dst}.{suffix}"
            print(f"{src} -> {dst} {is_valid_filename(dst)}")
            # os.rename(f"{video_dir}/{season_name}/{src}", f"{video_dir}/{season_name}/{dst}")
            count += 1

def rename_anime(config):
    # https://ja.wikipedia.org/wiki/
    with open(f"anime/{config}.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    video_dir = lines[0].strip()
    src_episode_list = sorted(os.listdir(video_dir))
    
    if len(src_episode_list) != len(lines[1:]):
        print(f"{config} episode number mismatch")
        return
    
    count = 1
    for src, dst in zip(src_episode_list, lines[1:]):
        suffix = src.split(".")[-1]
        dst = f"{dst.strip()}.{suffix}"
        print(f"{src} -> {dst} {is_valid_filename(dst)}")
        os.rename(f"{video_dir}/{src}", f"{video_dir}/{dst}")
        count += 1

def rename_drama(config):
    with open(f"drama/{config}.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    video_dir = lines[0].strip()
    src_episode_list = sorted(os.listdir(video_dir))
    
    if len(src_episode_list) != len(lines[1:]):
        print(f"{config} episode number mismatch")
        return
    
    count = 1
    for src, dst in zip(src_episode_list, lines[1:]):
        suffix = src.split(".")[-1]
        dst = f"{dst.strip()}.{suffix}"
        print(f"{src} -> {dst} {is_valid_filename(dst)}")
        os.rename(f"{video_dir}/{src}", f"{video_dir}/{dst}")
        count += 1

if __name__ == "__main__":
    # rename_tv_series("Friends")
    # rename_tv_series("The IT Crowd")
    # rename_tv_series("Yes,Minister&Yes,Prime.Minister")
    # rename_tv_series("How I Met Your Mother")
    
    # rename_anime("月刊少女野崎くん")
    # rename_anime("けいおん")
    rename_anime("氷菓")
    
    # rename_drama("半沢直樹")
    # rename_drama("アンナチュラル")