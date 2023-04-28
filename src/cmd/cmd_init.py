# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

import sys
import os

HERE = os.path.realpath(__file__)
CUR_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.dirname(CUR_DIR)

sys.path.append(OUT_DIR)

from form import FormInit


if __name__ == '__main__':
    form = FormInit()
    form.run()
