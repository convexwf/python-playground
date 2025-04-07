# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : ffmpeg_python/concat.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-04 16:08
# @UpdateTime : 2025-04-07 16:53

import os
import glob
import ffmpeg
import tempfile

# 配置
video_folder = "C:/Users/convexwf/OneDrive/documents/Language/Spanish/新东方西班牙语直通车/02.西班牙语欧标A1直通车(8课,99节全)/第一册 第01课"
output_video = "C:/Users/convexwf/Downloads/output.mp4"
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
    fps_str = video_stream["r_frame_rate"]  # e.g. "30/1"

    _format = probe["format"]
    duration = float(_format["duration"])  # in seconds

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


def concatenate_videos_with_same_codec(video_list, output_filename):
    """
    Concatenate a list of video files with the same codec into a single output file.

    Args:
        video_list (list): List of video file paths to concatenate.
        output_filename (str): Output file name for the concatenated video.
    """
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", delete=False, encoding="utf-8"
    ) as fp:
        for video in video_list:
            fp.write(f"file '{video}'\n")
        temp_file = fp.name

    try:
        ffmpeg.input(temp_file, format="concat", safe=0).output(
            output_filename
        ).global_args("-loglevel", "error").run(overwrite_output=True)
        print(f"Successfully created {output_filename}")
    except ffmpeg.Error as e:
        print(f"Error concatenating videos: {e}")


def classify_videos_by_duration(video_list, max_total_duration):
    """
    Classify a list of video files into groups where each group's total duration does not exceed max_total_duration.

    Args:
        video_list (list): List of video file paths.
        max_total_duration (int): Maximum total duration for each group in seconds.

    Returns:
        list: A list of lists, where each inner list contains video file paths.
    """
    categorized = []
    current_list = []
    current_time = 0

    for video in video_list:
        duration = get_video_info(video)["duration"]

        if current_time + duration > max_total_duration and current_list:
            categorized.append(current_list)
            current_list = []
            current_time = 0

        current_list.append(video)
        current_time += duration

    if current_list:
        categorized.append(current_list)

    return categorized
