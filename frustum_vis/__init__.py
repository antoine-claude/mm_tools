from .ops import FRUSTUMVIS_OT_update, FRUSTUMVIS_OT_toggle_auto
from .panel_menu import VIEW3D_PT_frustum_visibility
from .props import register_lod_properties, unregister_lod_properties
from .handler import ensure_handler, remove_handler

def get_frv_classes():
    return (
        FRUSTUMVIS_OT_update,
        FRUSTUMVIS_OT_toggle_auto,
        VIEW3D_PT_frustum_visibility,
    )
