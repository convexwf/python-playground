# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : ffmpeg_python/main.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-15 21:23
# @UpdateTime : 2025-04-15 21:23

import os
from concat import concatenate_videos_with_same_codec, classify_videos_by_duration

if __name__ == "__main__":
    video_root = "C:/Users/convexwf/OneDrive/documents/Language/Spanish/新东方西班牙语直通车/02.西班牙语欧标A1直通车(8课,99节全)/"
    output_root = "C:/Users/convexwf/Downloads/新东方西班牙语直通车/02.西班牙语欧标A1直通车(8课,99节全)/"
    for lesson_no, video_dir in enumerate(sorted(os.listdir(video_root))):
        video_folder = os.path.join(video_root, video_dir)
        if not os.path.isdir(video_folder):
            continue
        video_list = sorted(
            [
                os.path.join(video_folder, f)
                for f in os.listdir(video_folder)
                if f.endswith(".mp4")
            ]
        )

        categorized_videos = classify_videos_by_duration(
            video_list, max_total_duration=45 * 60
        )
        output_dir = os.path.join(output_root, video_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(
            f"Processing lesson {lesson_no + 1}: {video_dir} with {len(video_list)} videos"
        )
        for idx, categorized in enumerate(categorized_videos):
            if len(categorized) == 0:
                continue
            output_filename = os.path.join(
                output_dir, f"西语A1课程_{lesson_no + 1:02d}_{idx + 1:02d}.mp4"
            )
            print(
                f"Concatenating videos for {output_filename} with {len(categorized)} videos"
            )
            concatenate_videos_with_same_codec(categorized, output_filename)
