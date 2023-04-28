# -*- coding: utf-8 -*-


import math


X_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626  # π
A = 6378245.0  # 长半轴
EE = 0.00669342162296594323  # 偏心率平方
MERCATOR = 20037508.34 / 180.0
INITAL_RESOLUTION = 156543.03392
SIZE = 78271516


def is_in_china(func):
    def wrapper(lng, lat):
        if lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55:
            return func(lng, lat)
        return lng, lat
    return wrapper


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


@is_in_china
def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return mglng, mglat


@is_in_china
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return lng * 2 - mglng, lat * 2 - mglat


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * X_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * X_PI)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lng, bd_lat


def bd09_to_gcj02(bd_lng, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lng:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lng - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return gg_lng, gg_lat


def wgs84_to_bd09(lng, lat):
    lng, lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(lng, lat)


def bd09_to_wgs84(bd_lng, bd_lat):
    lng, lat = bd09_to_gcj02(bd_lng, bd_lat)
    return gcj02_to_wgs84(lng, lat)


# def lnglat_to_xyz(lng, lat, zoom):
#     lat_rad = math.radians(lat)
#     n = 2.0 ** zoom
#     xtile = int((lng + 180.0) / 360.0 * n)
#     ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
#     return xtile, ytile, zoom

def lnglat_to_xyz(lng, lat, level):
    n = 2 ** level
    x = int((lng + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / PI) / 2.0 * n)
    return x, y, level


def xyz_to_lnglat(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg, lat_deg
    # n = 2 ** z
    # lng = x / n * 360.0 - 180.0
    # lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    # lat = math.degrees(lat_rad)
    # return lng, lat


def lnglat_to_mercator(
    lng, lat,
    reference_lng=0, reference_lat=0,
    convert_rate=(1, 1)
):
    """
    将经纬度坐标二维展开为平面坐标
    :param lnglat: list[float] 经纬度
    :param reference_position: list 经纬度参照零点坐标，如城市中心或项目中心
    :param convert_rate: list 形变比例
    :return: list 展开后的二纬坐标，单位 m
    """
    x = lng - reference_lng
    y = lat - reference_lat

    x = x * MERCATOR
    y = math.log(math.tan((90 + y) *  PI / 360)) / ( PI / 180)
    y = y *  MERCATOR

    return x * convert_rate[0], y * convert_rate[1]


def mercator_to_lnglat(
    mx, my,
    reference_lng=0, reference_lat=0,
    convert_rate=(1, 1)
):
    """
    将平面座标回经纬度坐标
    :param mercator: list[float] 墨卡托 xy 坐标
    :param reference_position: list 经纬度参照零点坐标，如城市中心或项目中心
    :param convert_rate: list 形变比例
    :return: list 回归后的经纬度
    """

    x, y = mx / convert_rate[0], my / convert_rate[1]

    x, y = x / MERCATOR, y / MERCATOR
    y = 180 / PI * (2 * math.atan(math.exp(y * PI / 180)) - PI / 2)
    x += reference_lng
    y += reference_lat

    return x, y


# def zoom_to_size(zoom):
#     return SIZE * 2 ** (- zoom - 1)

def zoom_to_size(zoom):
    return INITAL_RESOLUTION / (2 ** zoom) * math.cos( math.pi / 180.0) * 256


__all__ = [
    "wgs84_to_gcj02",
    "gcj02_to_wgs84",
    "gcj02_to_bd09",
    "bd09_to_gcj02",
    "wgs84_to_bd09",
    "bd09_to_wgs84",
    "lnglat_to_xyz",
    "xyz_to_lnglat",
    "lnglat_to_mercator",
    "mercator_to_lnglat",
    "zoom_to_size"
]
