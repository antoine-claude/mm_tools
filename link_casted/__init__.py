# link_casted/__init__.py

import importlib
from . import (ops, panel_ui,)

# ---------REGISTER ----------.


def reload():
    global ops
    global panel_ui

    ops = importlib.reload(ops)
    panel_ui = importlib.reload(panel_ui)



def register():
    ops.register()
    panel_ui.register()


def unregister():
    ops.unregister()
    panel_ui.unregister()
    # Clean up dynamic Scene properties created by link_casted
    try:
        import bpy
        for prop in list(bpy.types.Scene.bl_rna.properties):
            if prop.identifier.startswith("link_"):
                delattr(bpy.types.Scene, prop.identifier)
    except Exception:
        pass
