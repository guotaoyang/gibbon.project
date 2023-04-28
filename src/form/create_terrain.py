# -*- coding: utf-8 -*-

import sys
import os
from System import Uri

HERE = os.path.realpath(__file__)
CUR_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.dirname(CUR_DIR)

sys.path.append(OUT_DIR)

import scriptcontext as sc
import Rhino

from Eto.Forms import Dialog, DialogResult, DynamicLayout
from Eto.Forms import TableCell, TableRow, TableLayout
from Eto.Forms import Panel, LinkButton
from Eto.Forms import DropDown, NumericStepper, CheckBox
from Eto.Forms import WebView, Label, ProgressBar
from Eto.Forms import Button, GroupBox, UITimer
from Eto.Drawing import Size, Padding
from ok_cancel_panel import OkCancelPanel

INNER_PADDING = Padding(10)
INNER_SPCAING = Size(5, 5)
GROUP_PADDING = Padding(10)
GROUP_SPACING = Size(10, 10)
MAP_STYLES = ['rgb', 'satellite']
spacer = Label()
spacer.Width = 20


class FormTerrain(Dialog[DialogResult]):
    """
    """

    def __init__(self, project):
        self.project = project

        self.Title = u"Gibbon"

        self.Minimizable = True
        self.Maximizable = True
        self.Resizable = True
        self.MinimumSize = Size(800, 600)

        self.timer = None
        self.counter = 0
        self._xyzs = list()
        self.label_map_info = Label(Text=self.project.map_info)
        self.setup()

    def setup(self):
        layout = TableLayout()
        layout.Padding = INNER_PADDING
        layout.Spacing = INNER_SPCAING

        cell_0 = TableCell(self.web_view, True)
        cell_1 = TableCell(self.setting_panel, False)
        layout.Rows.Add(TableRow(cell_0, cell_1))

        # Add a new row for the confirm_panel at the top-right

        self.Content = layout

    def confirm_panel(self):
        confirm_panel = Panel()
        layout = DynamicLayout()
        layout.Padding = Padding(left=0, top=20, right=0, bottom=10)
        layout.Spacing = Size(1, 1)

        # 使用 TableLayout 来实现右对齐
        table_layout = TableLayout()
        table_layout.Spacing = Size(5, 5)
        table_row = TableRow()
        spacer = Label()
        spacer.Width = 20
        table_row.Cells.Add(TableCell(self.new_ok_button, True))
        table_row.Cells.Add(TableCell(spacer, True, ScaleWidth=False))
        table_row.Cells.Add(TableCell(self.new_cancel_button, True))
        table_layout.Rows.Add(table_row)

        layout.Add(table_layout)
        confirm_panel.Content = layout
        return confirm_panel

    @property
    def setting_panel(self):
        panel = Panel()
        layout = TableLayout()
        layout.Padding = Padding(10)
        layout.Spacing = Size(5, 5)

        row1 = TableRow()
        row1.Cells.Add(TableCell(self.map_setting_groupbox, True))
        row1.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row1)

        row2 = TableRow()
        row2.Cells.Add(TableCell(self.label_map_info, True))
        row2.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row2)

        row3 = TableRow()
        row3.Cells.Add(TableCell(self.model_setting_group, True))
        row3.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row3)

        row4 = TableRow()
        row4.Cells.Add(TableCell(self.bar_panel(), True))
        row4.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row4)

        row5 = TableRow()
        row5.Cells.Add(TableCell(self.confirm_panel(), True))
        row5.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row5)
        
        row6 = TableRow()
        row6.Cells.Add(TableCell(None, False, ScaleWidth=False))
        layout.Rows.Add(row6)

        panel.Content = layout
        return panel

    def bar_panel(self):
        bar_panel = Panel()
        layout = DynamicLayout()
        layout.Padding = Padding(left=0, top=20, right=0, bottom=10)
        layout.Spacing = Size(5, 5)
        self.label_model_info = Label(Text=u'模型进度')
        self.bar = ProgressBar()
        spacer = Label()
        spacer.Width = 0
        layout.AddRow(self.label_model_info, spacer, self.bar)
        bar_panel.Content = layout
        return bar_panel

    @property
    def map_setting_groupbox(self):
        global GROUP_PADDING, GROUP_SPACING
        groupbox = GroupBox(Text=u'地图设置')

        layout = DynamicLayout()
        layout.Padding = GROUP_PADDING
        layout.Spacing = GROUP_SPACING

        label_texture_style = Label(Text=u'贴图样式:')
        self.dropdown_map_style = DropDown()
        self.dropdown_map_style.DataStore = MAP_STYLES
        self.dropdown_map_style.SelectedIndex = 0
        self.dropdown_map_style.SelectedIndexChanged += self.on_map_style

        label_map_zoom = Label(Text=u'地图等级:')
        self.number_map_zoom = NumericStepper()
        self.number_map_zoom.MaxValue = 18
        self.number_map_zoom.MinValue = 2
        self.number_map_zoom.Increment = 1
        self.number_map_zoom.DecimalPlaces = 0
        self.number_map_zoom.ValueChanged += self.on_zoom

        label_tile_quantity = Label(Text=u'数量:')
        self.number_tile_quantity = NumericStepper()
        self.number_tile_quantity.MaxValue = 10
        self.number_tile_quantity.MinValue = 2
        self.number_tile_quantity.Increment = 2
        self.number_tile_quantity.DecimalPlaces = 0
        self.number_tile_quantity.ValueChanged += self.on_tile_quantity

        layout.AddRow(label_texture_style, None, self.dropdown_map_style)
        layout.AddRow(label_map_zoom, None, self.number_map_zoom)
        layout.AddRow(label_tile_quantity, None, self.number_tile_quantity)

        groupbox.Content = layout

        return groupbox

    @property
    def model_setting_group(self):
        groupbox = GroupBox(Text=u'模型设置')

        layout = DynamicLayout()
        layout.Padding = GROUP_PADDING
        layout.Spacing = GROUP_SPACING

        label_mesh_density = Label(Text=u'网格密度:')
        self.number_mesh_density = NumericStepper()
        self.number_mesh_density.MaxValue = 100
        self.number_mesh_density.MinValue = 20
        self.number_mesh_density.Increment = 1
        self.number_mesh_density.DecimalPlaces = 0
        self.number_mesh_density.ValueChanged += self.on_mesh_density

        self.checkbox_building = CheckBox(Text=u'生成建筑')
        self.checkbox_building.Checked = True

        self.checkbox_road = CheckBox(Text=u'生成道路')
        self.checkbox_road.Checked = True

        label_folder = Label(Text=u'工作文件夹:')
        self.button_folder = Button(Text=u'选择')
        self.button_folder.Click += self.on_folder

        layout.AddRow(label_folder, None, self.button_folder)
        layout.AddRow(label_mesh_density, None, self.number_mesh_density)
        layout.AddRow(None, None, self.checkbox_building)
        layout.AddRow(None, None, self.checkbox_road)

        groupbox.Content = layout

        return groupbox

    @property
    def web_view(self):
        HERE = os.path.realpath(__file__)
        CUR_DIR = os.path.dirname(HERE)
        OUT_DIR = os.path.dirname(CUR_DIR)
        HTML_PATH = os.path.join(OUT_DIR, 'templates', 'index.html')

        web_view = WebView()
        web_view.Url = Uri(HTML_PATH)

        return web_view

    def on_ok(self, sender, e):
        if self.timer is None:
            self.timer = UITimer()
            self.timer.Interval = 0.1
            self.timer.Elapsed += self.update

            self._xyzs = self.project.calculate_xyzs()

            self.bar.MaxValue = len(self._xyzs)
            self.project.add_textdot()

            self.timer.Start()
            return None

        if self.timer.started:
            self.timer.Stop()

        else:
            self.timer.Start()

    def update(self, sender, e):
        try:
            xyz = self._xyzs[self.counter]
            self.project.create_terrain_by_xyz(xyz)

            self.counter += 1
            self.bar.Value = self.counter

        except Exception as error:
            print
            error
            self.end_thread()

        finally:
            if self.counter >= len(self.project.xyzs):
                self.counter = 0
                self.end_thread()
                self.Close(DialogResult.Ok)

    def end_thread(self):
        self.timer.Stop()
        self.timer.Dispose()
        self.timer = None

    @property
    def new_ok_button(self):
        button = Button()
        button.Text = "确认"
        button.Size = Size(40, 25)  # 设置按钮的大小
        button.Click += self.on_ok
        return button

    @property
    def new_cancel_button(self):
        button = Button()
        button.Text = "取消"
        button.Size = Size(40, 25)  # 设置按钮的大小
        button.Click += self.on_cancel  # 更改为正确的事件处理函数
        return button

    def on_cancel(self, sender, e):
        self.Close(DialogResult.Cancel)

    @property
    def link(self):
        button = LinkButton()
        button.Text = "Link"
        button.Click += self.on_link
        return button

    def on_link(self, sender, e):
        pass

    def run(self):
        self.ShowModalAsync(Rhino.UI.RhinoEtoApp.MainWindow)

    def on_map_style(self, sender, event):
        pass

    def on_zoom(self, sender, event):
        self.project.zoom = self.number_map_zoom.Value

    def on_map_style(self, sender, e):
        pass

    def on_zoom(self, sender, e):
        zoom_value = int(self.number_map_zoom.Value)
        self.project.zoom = zoom_value

    def on_tile_quantity(self, sender, e):
        tile_quantity = int(self.number_tile_quantity.Value)
        self.project.quantity = tile_quantity

    def on_mesh_density(self, sender, e):
        mesh_density = int(self.number_mesh_density.Value)
        self.project.density = mesh_density

    def on_folder(self, sender, e):
        folder = SelectFolderDialog().ShowDialog(Rhino.UI.RhinoEtoApp.MainWindow)
        if folder is not None: self.project.folder = folder

    def run(self):
        self.ShowModalAsync(Rhino.UI.RhinoEtoApp.MainWindow)


if __name__ == '__main__':
    # if is_init():
    project = sc.sticky['gibbon.project']
    FormTerrain(project).run()
