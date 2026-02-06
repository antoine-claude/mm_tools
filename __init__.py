from . import dependencies

dependencies.preload_modules()

import bpy
from .kitsu import (get_kitsu_classes,ensure_kitsu_handlers,remove_kitsu_handlers, register_kitsu_ui, register_kitsu_properties, unregister_kitsu_ui, unregister_kitsu_properties)
from . import (lighting, alert_path, anim_utils, frustum_vis, link_casted, build_shot, playblast_copy_montage)
from . import addon_updater_ops
from . import updater_ui
import importlib
importlib.reload(updater_ui)

bl_info = {
    "name": "MM Tools",
    "author": "Antoine C",
    "version": (0, 0, 8, 42),
}
def register():
    addon_updater_ops.register(bl_info)

    # register lighting package (registers its UI and classes)
    alert_path.register()
    anim_utils.register()
    build_shot.register()
    frustum_vis.register()
    lighting.register()
    link_casted.register()
    playblast_copy_montage.register()
    updater_ui.register()
    
    # Register all classes
    for cls_group in [ get_kitsu_classes()]:
        for cls in cls_group:
            bpy.utils.register_class(cls)
    
    # Register handlers
    ensure_kitsu_handlers()
    
    # Register properties and UI
    register_kitsu_ui()
    register_kitsu_properties()

def unregister():
    # Unregister properties first
    playblast_copy_montage.unregister()
    link_casted.unregister()
    lighting.unregister()
    frustum_vis.unregister()
    build_shot.unregister()
    anim_utils.unregister()
    alert_path.unregister()
    addon_updater_ops.unregister()
    updater_ui.unregister()


    # Unregister handlers
    remove_kitsu_handlers()
    unregister_kitsu_ui()
    unregister_kitsu_properties()
    
    # Unregister all classes in reverse order
    for cls_group in [get_kitsu_classes()]:
        for cls in reversed(cls_group):
            bpy.utils.unregister_class(cls)


