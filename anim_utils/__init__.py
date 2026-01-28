import importlib
from . import (op_append_last_frame, op_bake_pas2, op_control_version, op_libraries_remapper, op_save_increment,)

# ---------REGISTER ----------.


def reload():
    global ops_append_last_frame
    global op_bake_pas2
    global op_control_version
    global op_libraries_remapper
    global op_save_increment

    ui = importlib.reload(ui)
    ops_append_last_frame = importlib.reload(ops_append_last_frame)
    op_bake_pas2 = importlib.reload(op_bake_pas2)
    op_control_version = importlib.reload(op_control_version)
    op_libraries_remapper = importlib.reload(op_libraries_remapper)
    op_save_increment = importlib.reload(op_save_increment)



def register():
    op_append_last_frame.register()
    op_bake_pas2.register()
    op_control_version.register()
    op_libraries_remapper.register()
    op_save_increment.register()


def unregister():
    op_append_last_frame.unregister()
    op_bake_pas2.unregister()
    op_control_version.unregister()
    op_libraries_remapper.unregister()
    op_save_increment.unregister()
