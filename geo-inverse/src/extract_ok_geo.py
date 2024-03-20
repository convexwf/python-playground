# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : practice
# @FileName : extract_ok_geo.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-08 18:33
# @UpdateTime : TODO

import csv
import json
import os
from enum import Enum

csv.field_size_limit(2048576)

OUTPUT_JSON_DIR = os.environ.get("OUTPUT_JSON_DIR", "/tmp/city_info")
OK_GEO_CSV_PATH = os.path.join(OUTPUT_JSON_DIR, "ok_geo.csv")

CITY_JSON_DIR = os.path.join(OUTPUT_JSON_DIR, "output_city_info")

CHOOSE_CITY = {
    "beijing": "北京市",
    "shanghai": "上海市",
    "guangdong": "广东省",
    "zhejiang": "浙江省",
}


class CityType(Enum):
    NONE = "CITY_TYPE_NONE"
    PROVINCE = "CITY_TYPE_PROVINCE"  # 省
    MUNICIPALITY = "CITY_TYPE_MUNICIPALITY"  # 直辖市
    PREFECTURE = "CITY_TYPE_PREFECTURE"  # 地级市
    COUNTY = "CITY_TYPE_COUNTY"  # 县区
    TOWN = "CITY_TYPE_TOWN"  # 镇


def read_ok_geo_csv():
    lines = []
    with open(OK_GEO_CSV_PATH, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        # header: (id-行政区划ID, pid-父级行政区划ID, deep-行政级别, name-名称, ext_path-完整名称, geo-中心经纬度, polygon-边界)
        for row in csv_reader:
            xzqh_id = row[0]  # 行政区划ID
            deep = row[2]  # 0: 省 1: 市 2: 区 3：镇
            ext_path = row[4]  # 完整行政区划名称，以空格分隔 e.g 北京市 北京市 东城区
            geo = row[5]  # 中心经纬度，以空格分隔 GCJ-02坐标系
            polygon = row[
                6
            ]  # 边界集合，以;分隔，每个边界以,分隔，每个点以空格分隔经纬度 GCJ-02坐标系
            lines.append([xzqh_id, deep, ext_path, geo, polygon])
    return lines


def extract_geo(geo: str, ext_path: str):

    if geo == "EMPTY":
        print(f"Error: geo is empty, {ext_path}")
        return [0, 0]
    return [float(geo.split(" ")[0]), float(geo.split(" ")[1])]


def extract_mongo_polygon(polygons: str) -> dict:
    """extract mongodb supported polygon format from text.

    Args:
        polygons (_type_): _description_

    Returns:
        A multi-polygon dict object as mongodb supported format.
    """
    if polygons == "EMPTY":
        return {"type": "MultiPolygon", "coordinates": []}
    boundary_list = []
    for it in polygons.split(";"):
        points = it.split(",")
        boundary = []
        for point in points:
            point = point.strip().split(" ")
            boundary.append([float(point[0]), float(point[1])])
        boundary.append(boundary[0])
        boundary_list.append([boundary])
    return {"type": "MultiPolygon", "coordinates": boundary_list}


def extract_city_type(deep: str) -> CityType:
    """Get city type by deep

    Args:
        deep (str): 0: 省 1: 市 2: 区 3：镇

    Returns:
        CityType, e.g CityType.PROVINCE
    """
    if deep == "0":
        return CityType.PROVINCE
    if deep == "1":
        return CityType.MUNICIPALITY
    if deep == "2":
        return CityType.COUNTY
    if deep == "3":
        return CityType.TOWN
    return CityType.NONE


def extract_ext_path(ext_path: str):
    """extract primary_name, secondary_name, city_name from ext_path

    Args:
        ext_path (str): e.g 北京市 北京市 东城区

    Returns:
        (str, str, str): (primary_name, secondary_name, city_name)
    """
    ext_params = ext_path.split(" ")
    primary_name = ext_params[0]
    secondary_name = ext_params[1] if len(ext_params) > 1 else primary_name
    city_name = ext_params[2] if len(ext_params) > 2 else secondary_name
    return primary_name, secondary_name, city_name


def generate_city_json(lines, choose_city):
    city_list = []
    for line in lines:
        xzqh_id, deep, ext_path, geo, polygon = line
        primary_name, secondary_name, city_name = extract_ext_path(ext_path)
        if choose_city not in ext_path:
            continue
        city = {
            "city_id": f"{xzqh_id:0<6}",
            "city_name": city_name,
            "city_type": extract_city_type(deep).value,
            "country_name": "中国",
            "primary_name": primary_name,
            "secondary_name": secondary_name,
            "timezone": "Asia/Shanghai",
            "city_center": extract_geo(geo, ext_path),
            "city_boundary": extract_mongo_polygon(polygon),
        }
        city_list.append(city)
    return city_list


def main():
    os.makedirs(CITY_JSON_DIR, exist_ok=True)
    lines = read_ok_geo_csv()
    for city_en, city_cn in CHOOSE_CITY.items():
        print(f"extracting {city_cn} geo data from ok_geo.csv...")
        city_list = generate_city_json(lines, city_cn)
        with open(
            os.path.join(CITY_JSON_DIR, f"{city_en}.json"), "w+", encoding="utf-8"
        ) as f:
            f.write(json.dumps(city_list, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()
