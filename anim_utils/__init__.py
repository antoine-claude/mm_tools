import importlib
import bpy
from . import (op_append_last_frame, op_bake_pas2, op_control_version, op_libraries_remapper, op_save_increment, toolbar_menu, keymaps_and_menus)

# ---------REGISTER ----------.


def reload():
    global op_append_last_frame
    global op_bake_pas2
    global op_control_version
    global op_libraries_remapper
    global op_save_increment
    global toolbar_menu
    global keymaps_and_menus

    op_append_last_frame = importlib.reload(op_append_last_frame)
    op_bake_pas2 = importlib.reload(op_bake_pas2)
    op_control_version = importlib.reload(op_control_version)
    op_libraries_remapper = importlib.reload(op_libraries_remapper)
    op_save_increment = importlib.reload(op_save_increment)
    toolbar_menu = importlib.reload(toolbar_menu)
    keymaps_and_menus = importlib.reload(keymaps_and_menus)



def register():
    op_append_last_frame.register()
    op_bake_pas2.register()
    op_control_version.register()
    op_libraries_remapper.register()
    op_save_increment.register()
    toolbar_menu.register()
    keymaps_and_menus.register_keymaps()
    # Attach the File menu custom draw (centralized here to ensure both
    # modules are available when assigning)


def unregister():
    op_append_last_frame.unregister()
    op_bake_pas2.unregister()
    op_control_version.unregister()
    op_libraries_remapper.unregister()
    op_save_increment.unregister()
    toolbar_menu.unregister()
    keymaps_and_menus.unregister_keymaps()
