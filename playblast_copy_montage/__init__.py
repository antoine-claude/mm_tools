import importlib
from . import ops, ui, props

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
    ops.unregister()
    ui.unregister()
    props.unregister()
