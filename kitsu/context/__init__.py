# SPDX-FileCopyrightText: 2021 Blender Studio Tools Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
from ..context import ui


# ---------REGISTER ----------.


def reload():
    global ui

    ui = importlib.reload(ui)


def register():
    ui.register()


def unregister():
    ui.unregister()
