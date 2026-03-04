import importlib
from . import ops, panel

# ---------REGISTER ----------.


def reload():
    global ops
    global panel

    ops = importlib.reload(ops)
    panel = importlib.reload(panel)


def register():
    ops.register()
    panel.register()


def unregister():
    panel.unregister()
    ops.unregister()
