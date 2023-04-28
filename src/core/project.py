# -*- coding: utf-8 -*-


import os
import json

from Rhino.Geometry import Point3d
import rhinoscriptsyntax as rs
import scriptcontext as sc


from gis import CoordSys, LngLat, XYZ
from mapbox import Mapbox
from terrain import Terrain


class Project(object):
    def __init__(self, doc=sc.doc):
        self.doc = doc
        # 28.12639858046898, 112.90893924628702
        self.lnglat = LngLat(112.908939, 28.126398)
        self.zoom = 18

        self.quantity = 4
        self.density = 40

        self._folder = None
        self._mapbox = Mapbox('vctcn93')

    def __repr__(self):
        info = "Project:\n"
        info += "\tlnglat: {}\n".format(self.lnglat)
        info += "\txyz: {}\n".format(self.xyz)
        info += "\torigin: {}\n".format(self.origin)
        info += "\treal origin mercator: {}\n".format(self.real_origin_mercator)
        info += "\ttag mercator: {}\n".format(self.tag_mercator)
        return info

    @property
    def xyz(self):
        return self.lnglat.to_xyz(self.zoom)

    @property
    def origin(self):
        return self.xyz.to_lnglat()

    @property
    def real_origin_mercator(self):
        return self.origin.to_mercator()

    @property
    def tag_mercator(self):
        return self.lnglat.to_mercator() - self.real_origin_mercator

    @property
    def terrain_path(self):
        return "Gibbon::Terrain::zoom {}".format(self.zoom)

    @property
    def building_path(self):
        return "Gibbon::Terrain::zoom {}".format(self.zoom)

    @property
    def folder(self):
        if self._folder is None:
            gibbon_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Gibbon")
            if not os.path.exists(gibbon_folder): os.mkdir(gibbon_folder)
            self._folder = gibbon_folder
        return self._folder

    @folder.setter
    def folder(self, value):
        self._folder = value

    @property
    def map_info(self):
        return 

    @property
    def model_info(self):
        return 

    @property
    def bounds(self):
        # min_x = self.xyz.x - self.quantity / 2
        # min_y = self.xyz.y - self.quantity / 2
        # max_x = self.xyz.x + self.quantity / 2
        # max_y = self.xyz.y + self.quantity / 2

        # min_mercator = Mercator(min_x * self.tile_size, min_y * self.tile_size)
        # max_mercator = Mercator(max_x * self.tile_size, max_y * self.tile_size)

        # real_min_mercator = min_mercator + self.real_origin_mercator
        # real_max_mercator = max_mercator + self.real_origin_mercator

        # return real_min_mercator.to_lnglat(), real_max_mercator.to_lnglat()
        pass

    def calculate_xyzs(self):
        xyzs = list()
        x_start = self.xyz.x - self.quantity / 2
        y_start = self.xyz.y - self.quantity / 2 + 1

        for i in range(self.quantity):
            for j in range(self.quantity):
                x = x_start + i
                y = y_start + j
                xyzs.append(XYZ(x, y, self.xyz.z))

        return xyzs

    def create_terrain_by_xyz(self, xyz):
        dem_path = self._mapbox.download_image(xyz, 0, self.folder)
        texture_path = self._mapbox.download_image(xyz, 1, self.folder)

        terrain = Terrain(xyz, dem_path, texture_path)
        terrain.create_mesh(self.density)
        terrain.adjust_size()
        terrain.adjust_position(self.xyz)
        terrain.set_layer_path(self.terrain_path)
        terrain.bake(self.doc)
        terrain.add_texture(self.doc)

    def add_textdot(self):
        point = Point3d(self.tag_mercator.x, self.tag_mercator.y, 0)
        rs.AddTextDot(u"项目位置", point)

    def dump_settings(self):
        settings = dict(
            lng=self.lnglat.lng,
            lat=self.lnglat.lat,
            zoom=self.zoom,
            quantity=self.quantity
        )

        HERE = os.path.dirname(__file__)
        CORE_DIR = os.path.dirname(HERE)
        ROOT = os.path.dirname(CORE_DIR)
        # ROOT = os.path.dirname(SRC_DIR)

        print ROOT

        with open(os.path.join(ROOT, "data", "settings.json"), "w") as f:
            json.dump(settings, f, indent=4)


if __name__ == '__main__':
    project = Project()
    project.dump_settings()
    xyzs = project.calculate_xyzs()
    for xyz in xyzs: project.create_terrain_by_xyz(xyz)
    project.add_textdot()
    print("Finished!")
    # print project
