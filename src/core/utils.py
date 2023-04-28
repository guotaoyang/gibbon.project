# -*- coding: utf-8 -*-


from Rhino.Geometry import Interval, Plane, Transform
from Rhino.DocObjects import Layer
from Rhino.Render import TextureMapping, RenderMaterial


class Util:
    """
    """

    @staticmethod
    def remap_mesh_coordinate(mesh):
        boundingbox = mesh.GetBoundingBox(True)

        x_domain = Interval(boundingbox.Min.X, boundingbox.Max.X)
        y_domain = Interval(boundingbox.Min.Y, boundingbox.Max.Y)
        z_domian = Interval(0.0, 1.0)

        tm = TextureMapping.CreatePlaneMapping(Plane.WorldXY, x_domain, y_domain, z_domian)
        mesh.SetTextureCoordinates(tm, Transform.Unset, False)

        return mesh

    @staticmethod
    def create_render_material(doc, material_name, material_path):
        material_index = doc.Materials.Find(material_name, True)

        if material_index == -1:
            material_index = doc.Materials.Add()

            material = doc.Materials[material_index]
            material.Name = material_name

            material.SetBitmapTexture(str(material_path))
            render_material = RenderMaterial.CreateBasicMaterial(material, doc)
            doc.RenderMaterials.Add(render_material)

            return render_material

        return doc.Materials[material_index].RenderMaterial

    @classmethod
    def layer_by_full_path(cls, doc, full_path):
        """
        根据图层路径创建图层
        """
        layer_index = doc.Layers.FindByFullPath(full_path, -2)

        if layer_index < 0 :
            layernames = full_path.rpartition("::");
            layer = Layer()

            if layernames[0] != "":
                parent_index = cls.layer_by_full_path(doc, layernames[0])
                layer.ParentLayerId = doc.Layers[parent_index].Id

            layer.Name = layernames[2]
            layer_index = doc.Layers.Add(layer)

        return layer_index

    @staticmethod
    def delete_objects_in_layer(doc, full_path):
        layer_index = doc.Layers.FindByFullPath(full_path, True)

        for obj in doc.Objects:
            if obj.Attributes.LayerIndex == layer_index:
                doc.Objects.Delete(obj)
