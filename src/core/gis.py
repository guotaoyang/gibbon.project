# -*- coding: utf-8 -*-


# from enum import Enum

from Rhino.Geometry import Point3d
from convertor import *


class CoordSys(object):
    """
    """

    WGS84 = 1
    GCJ02 = 2
    BD09 = 3


class XYZ(object):
    """
    """

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    def __sub__(self, other):
        return XYZ(self._x - other.x, self._y - other.y, self._z - other.z)

    def __add__(self, other):
        return XYZ(self._x + other.x, self._y + other.y, self._z + other.z)

    def __mul__(self, other):
        return XYZ(self._x * other, self._y * other, self._z * other)

    def __getitem__(self, item):
        if item == 0:
            return self._x
        elif item == 1:
            return self._y
        elif item == 2:
            return self._z
        else:
            raise IndexError

    def __repr__(self):
        return "XYZ({}, {}, {})".format(self._x, self._y, self._z)

    def to_list(self):
        return [self._x, self._y, self._z]

    def to_lnglat(self):
        lng, lat = xyz_to_lnglat(self._x, self._y, self._z)
        return LngLat(lng, lat)


class Mercator(object):
    """
    """

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __sub__(self, other):
        return Mercator(self._x - other.x, self._y - other.y)

    def __add__(self, other):
        return Mercator(self._x + other.x, self._y + other.y)

    def __getitem__(self, item):
        if item == 0:
            return self._x
        elif item == 1:
            return self._y
        else:
            raise IndexError

    def __repr__(self): 
        return "Mercator({}, {})".format(self._x, self._y)

    def to_lnglat(self):
        lng, lat = mercator_to_lnglat(self._x, self._y)
        return LngLat(lng, lat)

    def to_point3d(self):
        return Point3d(self._x, self._y, 0)


class LngLat(object):
    """
    """

    def __init__(self, lng, lat, coord_sys=CoordSys.WGS84):
        self._lng = lng
        self._lat = lat
        self._coord_sys = coord_sys

    def __repr__(self):
        return "LngLat({}, {})".format(self._lng, self._lat)

    @property
    def lng(self):
        return self._lng

    @property
    def lat(self):
        return self._lat

    @property
    def coord_sys(self):
        return self._coord_sys

    @coord_sys.setter
    def coord_sys(self, coord_sys):

        if self._coord_sys == CoordSys.WGS84:
            if coord_sys == CoordSys.GCJ02:
                self._lng, self._lat = wgs84_to_gcj02(self._lng, self._lat)

            elif coord_sys == CoordSys.BD09:
                self._lng, self._lat = wgs84_to_bd09(self._lng, self._lat)

        elif self._coord_sys == CoordSys.GCJ02:
            if coord_sys == CoordSys.WGS84:
                self._lng, self._lat = gcj02_to_wgs84(self._lng, self._lat)

            elif coord_sys == CoordSys.BD09:
                self._lng, self._lat = gcj02_to_bd09(self._lng, self._lat)

        elif self._coord_sys == CoordSys.BD09:
            if coord_sys == CoordSys.WGS84:
                self._lng, self._lat = bd09_to_wgs84(self._lng, self._lat)

            elif coord_sys == CoordSys.GCJ02:
                self._lng, self._lat = bd09_to_gcj02(self._lng, self._lat)

        self._coord_sys = coord_sys

    def to_xyz(self, zoom):
        x, y, z = lnglat_to_xyz(self.lng, self.lat, zoom)
        return XYZ(x, y, z)

    def to_mercator(self):
        x, y = lnglat_to_mercator(self.lng, self.lat)
        return Mercator(x, y)
