from .op_bake_pas2 import *
from .op_libraries_remapper import *
from .op_append_last_frame import *

from .op_save_increment import *
from ..updater_ui import *


# facultatif : une liste globale des classes si tu veux
def get_anim_utils_classes():
    from .op_bake_pas2 import classes as bake_anim_classes
    from .op_libraries_remapper import classes as libraries_remapper_classes
    from .op_append_last_frame import classes as last_frame_classes
    from .op_save_increment import classes as save_classes
    from ..updater_ui import classes as draw_update_classes


    return bake_anim_classes + libraries_remapper_classes + last_frame_classes + save_classes + draw_update_classes