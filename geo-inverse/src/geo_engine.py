# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : geo-inverse
# @FileName : geo_engine.py
# @Author : convexwf@gmail.com
# @CreateDate : 2024-05-11 14:27
# @UpdateTime : TODO

import argparse
import json
import os
from enum import Enum
from typing import List, Tuple

from mongoengine import (
    Document,
    EnumField,
    GeoPointField,
    MultiPolygonField,
    StringField,
    connect,
)

OUTPUT_JSON_DIR = os.environ.get("OUTPUT_JSON_DIR", "/tmp/city_info")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27086")
CITY_JSON_DIR = os.path.join(OUTPUT_JSON_DIR, "output_city_info")

connect(host=MONGO_URI, db="geo", connectTimeoutMS=1000)


class CityType(Enum):
    NONE = "CITY_TYPE_NONE"
    PROVINCE = "CITY_TYPE_PROVINCE"  # 省
    MUNICIPALITY = "CITY_TYPE_MUNICIPALITY"  # 直辖市
    PREFECTURE = "CITY_TYPE_PREFECTURE"  # 地级市
    COUNTY = "CITY_TYPE_COUNTY"  # 县
    TOWN = "CITY_TYPE_TOWN"  # 镇


class CityInfo(Document):
    __tablename__ = "city_info"
    city_id = StringField(required=True, primary_key=True)
    city_name = StringField(required=True)
    city_type = EnumField(CityType, required=True)
    country_name = StringField()
    primary_name = StringField()
    secondary_name = StringField()
    timezone = StringField()
    city_center = GeoPointField()
    city_boundary = MultiPolygonField()

    meta = {
        "indexes": [
            {
                "fields": [("city_type", 1), ("city_boundary", "2dsphere")],
            },
        ]
    }


def import_geo_data():
    """Import geo data from json files.

    Extract the city information from the json files and save them to the MongoDB.

    """
    print("Start importing geo data...")
    if not os.path.exists(CITY_JSON_DIR):
        print(f"Error: {CITY_JSON_DIR} not exists.")
        os._exit(1)
    json_files = os.listdir(CITY_JSON_DIR)
    for json_file in json_files:
        if not json_file.endswith(".json"):
            continue
        print(f"Waiting for import {json_file}...")
        with open(os.path.join(CITY_JSON_DIR, json_file), "r") as f:
            city_info_list = json.load(f)
        for city_info in city_info_list:
            CityInfo(**city_info).save()
    print("Geo data imported successfully.")


def check_lat_lng(lat: float, lng: float) -> bool:
    """Check if the latitude and longitude are valid.

    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.

    Returns:
        bool: True if the latitude and longitude are valid, otherwise False.
    """
    if -90 <= lat <= 90 and -180 <= lng <= 180:
        return True
    return False


def get_city_info_by_lat_lng(lat: float, lng: float) -> dict:
    """Get city information by latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.

    Returns:
        dict: City information.
    """
    if not check_lat_lng(lat, lng):
        return {}
    city_info = CityInfo.objects(
        city_boundary__geo_intersects=[lng, lat], city_type=CityType.COUNTY
    ).first()
    return city_info.to_mongo().to_dict() if city_info else {}


def batch_get_city_info_by_lat_lng(
    lat_lng_list: List[Tuple[float, float]]
) -> List[dict]:
    """Get city information by latitude and longitude.

    Args:
        lat_lng_list (List[Tuple[float, float]]): List of latitude and longitude of the locations.

    Returns:
        List[dict]: List of city information.
    """
    city_info_list = []
    for lat, lng in lat_lng_list:
        city_info_list.append(get_city_info_by_lat_lng(lat, lng))
    return city_info_list


def main():
    parser = argparse.ArgumentParser(description="Geo Engine")
    parser.add_argument(
        "--import_geo_data",
        action="store_true",
        help="Import geo data from json files.",
    )
    parser.add_argument("--lat", type=float, help="Latitude of the location.")
    parser.add_argument("--lon", type=float, help="Longitude of the location.")
    parser.add_argument("-f", "--file", type=str, help="Input file path.")
    parser.add_argument("-o", "--output", type=str, help="Output csv file path.")
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode."
    )
    args = parser.parse_args()

    if args.import_geo_data:
        import_geo_data()
    elif args.lat and args.lon:
        city_info = get_city_info_by_lat_lng(args.lat, args.lon)
        if len(city_info) == 0:
            print("No city information found. Maybe you should update the geo data.")
        else:
            print(
                f"ID: {city_info.get('_id')}, Name: {city_info.get('primary_name')}{city_info.get('secondary_name')}{city_info.get('city_name')}"
            )
    elif args.file and args.output:
        with open(args.file, "r") as f:
            lat_lng_list = [
                tuple(map(float, line.strip().split(","))) for line in f.readlines()
            ]
        city_info_list = batch_get_city_info_by_lat_lng(lat_lng_list)
        with open(args.output, "w+", encoding="utf-8") as f:
            f.write("latlon(WGS84),ID,Name\n")
            for latlon, city_info in zip(lat_lng_list, city_info_list):
                f.write(
                    f"{latlon[0]},{latlon[1]},{city_info.get('primary_name')}{city_info.get('secondary_name')}{city_info.get('city_name')}\n"
                )
    elif args.interactive:
        while True:
            lat = float(input("Please input the latitude of the location: "))
            lng = float(input("Please input the longitude of the location: "))
            city_info = get_city_info_by_lat_lng(lat, lng)
            if len(city_info) == 0:
                print(
                    "No city information found. Maybe you should update the geo data."
                )
            else:
                print(
                    f"ID: {city_info.get('_id')}, Name: {city_info.get('primary_name')}{city_info.get('secondary_name')}{city_info.get('city_name')}"
                )
            if input("Continue? (Y/n): ").lower() == "n":
                break
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
