# -*- coding: utf-8 -*-

import sys
import os

HERE = os.path.realpath(__file__)
CUR_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.dirname(CUR_DIR)

sys.path.append(OUT_DIR)

import scriptcontext as sc
import Rhino

from Eto.Forms import Dialog, DialogResult
from Eto.Forms import DynamicLayout, Panel, TextArea
from Eto.Forms import Label, Button, LinkButton
from Eto.Forms import MessageBox, MessageBoxType
from Eto.Drawing import Size, Padding

from ok_cancel_panel import OkCancelPanel
from core import Project


class FormInit(Dialog[DialogResult]):
    """
    """

    def __init__(self):
        self.Title = u"Gibbon"
        self.Padding = Padding(5)
        self.Resizable = False

        layout = DynamicLayout()
        layout.Spacing = Size(5, 5)

        layout.AddRow(self.info)
        layout.AddRow(self.panel)

        self.Content = layout

    @property
    def info(self):
        msg = """
        欢迎使用 Gibbon:
        在使用本程序前，请点击确定，初始化程序本程序...\t
        """
        label = Label()
        label.Text = msg
        return label

    @property
    def ok(self):
        button = Button(Text=u'确定')
        button.Click += self.on_ok
        return button

    def on_ok(self, sender, event):
        try:
            self.inital_project()
            print u"Gibbon 初始化成功!"
            self.Close(DialogResult.Ok)

        except Exception as e:
            msg = u"程序初始化失败，请联系开发者以获得帮助:\n"
            msg += str(e)

            MessageBox.Show(msg, "Gibbon", MessageBoxType.Error)
            self.Close(DialogResult.No)

    @property
    def cancel(self):
        button = Button(Text=u'取消')
        button.Click += self.on_cancel
        return button

    def on_cancel(self, sender, event):
        self.Close(DialogResult.Cancel)

    @property
    def link(self):
        link = LinkButton(Text=u'了解更多...')
        link.Click += self.on_link
        return link

    def on_link(self, sender, event):
        pass

    @property
    def panel(self):
        panel = OkCancelPanel.from_ok_cancel(self.ok, self.cancel, self.link)
        return panel

    @staticmethod
    def inital_project():
        project = Project()
        sc.sticky["gibbon.project"] = project
        project.dump_settings()

    def run(self):
        self.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)


if __name__ == '__main__':
    form = FormInit()
    form.run()
