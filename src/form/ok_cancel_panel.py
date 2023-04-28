# -*- coding: utf-8 -*-

from Eto.Forms import Panel, Label
from Eto.Forms import DynamicLayout
from Eto.Drawing import Size, Padding


class OkCancelPanel(Panel):

    @classmethod
    def from_ok_cancel(cls, ok, cancel, link_button):
        panel = cls()
        panel.ok = ok
        panel.cancel = cancel
        panel.link_button = link_button
        panel.setup()
        return panel

    def setup(self):
        layout = DynamicLayout()
        layout.Padding = Padding(5)
        layout.Spacing = Size(10, 10)
        layout.AddRow(None, Label(), self.link_button)
        layout.AddRow(None, self.ok, self.cancel)
        self.Content = layout