# -*- coding: utf-8 -*-

import sys
import os

import scriptcontext as rs

HERE = os.path.realpath(__file__)
CUR_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.dirname(CUR_DIR)

sys.path.append(OUT_DIR)

from forms import FormTerrain


def main(is_init):
    if is_init:
        project = rs.sticky['gibbon.project']
        form = FormTerrain(project)
        form.run()
