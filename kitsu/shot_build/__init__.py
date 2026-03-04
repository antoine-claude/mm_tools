# SPDX-FileCopyrightText: 2021 Blender Studio Tools Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
from ..shot_build import ops, ui, props


# ---------REGISTER ----------.


def reload():
    global ops
    global ui
    global props

    ops = importlib.reload(ops)
    ui = importlib.reload(ui)
    props = importlib.reload(props)

def register():
    ops.register()
    ui.register()
    props.register()


def unregister():
    props.unregister()
    ui.unregister()
    ops.unregister()
