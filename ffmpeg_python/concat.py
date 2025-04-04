# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : ffmpeg_python/concat.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-04 16:08
# @UpdateTime : 2025-04-04 16:08

import os
import glob
import ffmpeg

# 配置
video_folder = "C:/Users/convexwf/OneDrive/documents/Language/Spanish/新东方西班牙语直通车/02.西班牙语欧标A1直通车(8课,99节全)/第一册 第01课"
output_video = "西语A1课程_01.mp4"
max_duration = 3600  # 1小时，秒


def get_video_info(filepath):
    """
    Get video codec, resolution, duration, and frames per second (fps) from a video file.

    Args:
        filepath (str): Path to the video file.

    Returns:
        dict: A dictionary containing codec, width, height, fps, and duration of the video.
    """
    probe = ffmpeg.probe(filepath)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )

    if not video_stream:
        raise Exception("No video stream found")

    codec = video_stream["codec_name"]
    width = int(video_stream["width"])
    height = int(video_stream["height"])
    duration = float(video_stream["duration"])  # in seconds
    fps_str = video_stream["r_frame_rate"]  # e.g. "30/1"

    # Calculate frames per second (fps)
    num, denom = map(int, fps_str.split("/"))
    fps = num / denom

    return {
        "codec": codec,
        "width": width,
        "height": height,
        "fps": fps,
        "duration": duration,
    }


def concatenate_video_list(video_list, output_filename):
    """
    Concatenate a list of video files into a single output file.

    Args:
        video_list (list): List of video file paths to concatenate.
        output_filename (str): Output file name for the concatenated video.
    """
    inputs = [ffmpeg.input(f) for f in video_list]
    # Use concatenation filter to join videos (assuming same codec)
    joined = ffmpeg.concat(*inputs, v=1, a=1).output(output_filename)
    try:
        ffmpeg.run(joined, overwrite_output=True)
        print(f"Successfully created {output_filename}")
    except ffmpeg.Error as e:
        print(f"Error concatenating videos: {e}")


def classify_videos_by_duration(files, max_total_duration):
    """将视频列表按时长分类，每段不超过 max_total_duration"""
    categorized = []
    current_list = []
    current_time = 0

    for file in files:
        duration = get_video_duration(file)

        if current_time + duration > max_total_duration and current_list:
            # 超过限制，保存当前列表
            categorized.append(current_list)
            current_list = []
            current_time = 0

        current_list.append(file)
        current_time += duration

    # 添加最后一组
    if current_list:
        categorized.append(current_list)

    return categorized


def main():
    files = sorted(glob.glob(os.path.join(video_folder, "*.mp4")))
    categorized_lists = classify_videos_by_duration(files, max_duration)

    for idx, video_list in enumerate(categorized_lists, start=1):
        output_file = f"{output_prefix}{idx}.mp4"
        concatenate_video_list(video_list, output_file)


if __name__ == "__main__":
    # for video in sorted(os.listdir(video_folder)):
    #     if video.endswith(".mp4"):
    #         print(
    #             f"Found video: {video} duration: {get_video_duration(os.path.join(video_folder, video))} seconds"
    #         )
    video_list = sorted(glob.glob(os.path.join(video_folder, "*.mp4")))[:10]
    for video in video_list:
        vedio_info = get_video_info(video)
        print(f"Video: {video}, Info: {vedio_info}")
    # output_video = os.path.join(video_folder, output_video)
    # concatenate_video_list(video_list, output_video)
