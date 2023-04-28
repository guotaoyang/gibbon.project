# -*- coding: utf-8 -*-


from System.Drawing import Bitmap


from Rhino.Geometry import Mesh, Point3d, Plane, Transform, Vector3d
from Rhino.DocObjects import ObjectAttributes


from utils import Util
from convertor import zoom_to_size


INITAL_RESOLUTION = 156543.03392  # 瓦片初始分辨率


class Terrain(object):
    def __init__(self, xyz, dem_path, texture_path=None):
        self._xyz = xyz
        self.dem_path = dem_path
        self.texture_path = texture_path

        self.layer_path = "Default"
        self._mesh = None
        self._mesh_id = None

    @property
    def xyz(self):
        return self._xyz

    @property
    def index(self):
        return "{}-{}-{}".format(self.xyz.x, self.xyz.y, self.xyz.z)

    @property
    def object_name(self):
        return "terrain:{}".format(self.index)

    @property
    def materinal_name(self):
        return "satelltite:{}".format(self.index)

    @property
    def zoom(self):
        return self.xyz.z

    @property
    def size(self):
        return zoom_to_size(self.zoom)

    def _create_points(self, density=20):
        """
        创建点矩阵
        """
        def rgb_to_height(r, g, b):
            return (r * 256 * 256 + g * 256 + b) * 0.1 - 10000

        def slice_group(total, quantity):
            """
            将 0-total 均分为 quantity 段
            """
            step = total / (quantity - 1)
            return [int(step * i) for i in range(quantity)]

        dem = Bitmap(self.dem_path)
        indices = slice_group(dem.Width - 1, density)
        results = list()

        for i in indices:
            row = list()

            for j in indices:
                color = dem.GetPixel(i, j)
                height = rgb_to_height(color.R, color.G, color.B)
                point = Point3d(i, dem.Height - j - 1, height)
                row.append(point)

            results.append(row)

        return results

    def create_mesh(self, density=20):
        mesh = Mesh()
        points = self._create_points(density)

        for i in range(len(points) - 1):
            for j in range(len(points[i]) - 1):
                sub_mesh = Mesh()

                p1 = points[i][j]
                p2 = points[i][j + 1]
                p3 = points[i + 1][j + 1]
                p4 = points[i + 1][j]

                sub_mesh.Vertices.Add(p1)
                sub_mesh.Vertices.Add(p2)
                sub_mesh.Vertices.Add(p3)
                sub_mesh.Vertices.Add(p4)

                sub_mesh.Faces.AddFace(0, 1, 2, 3)

                mesh.Append(sub_mesh)

        self._mesh = mesh

    def adjust_size(self, pixel=512):
        scale_size = self.size / (pixel - 1)
        scale = Transform.Scale(Plane.WorldXY, scale_size, scale_size, 1)
        self._mesh.Transform(scale)

    def adjust_position(self, project_origin_xyz):
        x = (self.xyz.x - project_origin_xyz.x) * self.size
        y = (project_origin_xyz.y - self.xyz.y) * self.size
        movement = Vector3d(x, y, 0)
        self._mesh.Translate(movement)

    def set_layer_path(self, layer_path):
        self.layer_path = layer_path

    def create_attribute(self, doc):
        layer_index = Util.layer_by_full_path(doc, self.layer_path)

        attr = ObjectAttributes()
        attr.Name = self.object_name
        attr.LayerIndex = layer_index

        return attr

    def bake(self, doc):
        if self._mesh is not None:
            attr = self.create_attribute(doc)
            mesh = Util.remap_mesh_coordinate(self._mesh)
            self._mesh_id = doc.Objects.AddMesh(mesh, attr)

    def add_texture(self, doc):
        if self._mesh_id is not None:
            render_mat = Util.create_render_material(doc, self.materinal_name, self.texture_path)
            mesh_obj = doc.Objects.FindId(self._mesh_id)
            mesh_obj.RenderMaterial = render_mat
            mesh_obj.CommitChanges()
