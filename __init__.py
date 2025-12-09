from . import dependencies

dependencies.preload_modules()

import bpy
from .anim_utils import ( get_anim_utils_classes )
from .toolbar_menu import VIEW3D_MT_MM
from .keymaps_and_menus import ( custom_file_menu_draw, register_keymaps, unregister_keymaps )
from .frustum_vis import ( get_frv_classes, register_frustum_properties, unregister_frustum_properties, ensure_frustum_handler, remove_frustum_handler )
from .link_casted import (get_link_casted_classes)
from .alert_path import (get_alert_path_classes, ensure_alert_handlers, remove_alert_handlers, draw_alert_menu)
from . import addon_updater_ops

bl_info = {
    "name": "MM Menu",
    "version": (0, 0, 6),
}

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_MM")
    
def register():
    addon_updater_ops.register(bl_info)
    
    # Register all classes
    for cls_group in [get_anim_utils_classes(), get_frv_classes(), 
                      get_link_casted_classes(), get_alert_path_classes()]:
        for cls in cls_group:
            bpy.utils.register_class(cls)
    
    # Register handlers
    ensure_frustum_handler()
    ensure_alert_handlers()
    
    # Register UI
    bpy.utils.register_class(VIEW3D_MT_MM)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_alert_menu)
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    bpy.types.TOPBAR_MT_file.draw = custom_file_menu_draw
    
    # Register keymaps and properties
    register_frustum_properties()
    register_keymaps()

def unregister():
    # Unregister keymaps and properties first
    unregister_keymaps()
    unregister_frustum_properties()
    
    # Unregister UI
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_alert_menu)
    if hasattr(bpy.types.TOPBAR_MT_file, "draw"):
        del bpy.types.TOPBAR_MT_file.draw
    bpy.utils.unregister_class(VIEW3D_MT_MM)
    
    # Unregister handlers
    remove_frustum_handler()
    remove_alert_handlers()
    
    # Unregister all classes in reverse order
    for cls_group in [get_alert_path_classes(), get_link_casted_classes(),
                      get_frv_classes(), get_anim_utils_classes()]:
        for cls in reversed(cls_group):
            bpy.utils.unregister_class(cls)
    
    # Clean up dynamic properties
    for prop in list(bpy.types.Scene.bl_rna.properties):
        if prop.identifier.startswith("link_"):
            delattr(bpy.types.Scene, prop.identifier)

    addon_updater_ops.unregister()