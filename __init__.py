from . import dependencies

dependencies.preload_modules()

import bpy
from .anim_utils import ( get_anim_utils_classes )
from .toolbar_menu import VIEW3D_MT_MM
from .keymaps_and_menus import ( custom_file_menu_draw, register_keymaps, unregister_keymaps )
from .frustum_vis import ( get_frv_classes, register_frustum_properties, unregister_frustum_properties, ensure_handler, remove_handler )
from .link_casted import (get_link_casted_classes)
from . import addon_updater_ops

bl_info = {
    "name": "MM Menu",
    "version": (0, 0, 5),
}

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_MM")
    
def register():
    addon_updater_ops.register(bl_info)
    # Register operators from ops/
    for cls in get_anim_utils_classes():
        bpy.utils.register_class(cls)

    for cls in get_frv_classes():
        bpy.utils.register_class(cls)  

    for cls in get_link_casted_classes():
        bpy.utils.register_class(cls)

    ensure_handler()
    # Register menus
    bpy.utils.register_class(VIEW3D_MT_MM)
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    bpy.types.TOPBAR_MT_file.draw = custom_file_menu_draw

    # Register keymaps
    register_frustum_properties()
    register_keymaps()

def unregister():

    # Unregister menus
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)
    if hasattr(bpy.types.TOPBAR_MT_file, "draw"):
        del bpy.types.TOPBAR_MT_file.draw
    bpy.utils.unregister_class(VIEW3D_MT_MM)

    for cls in reversed(get_frv_classes()):
        bpy.utils.unregister_class(cls)
    remove_handler()
    # Unregister operators (in reverse)
    for cls in reversed(get_anim_utils_classes()):
        bpy.utils.unregister_class(cls)


    # Supprime les propriétés dynamiques
    for prop in bpy.types.Scene.bl_rna.properties:
        if prop.identifier.startswith("link_"):
            delattr(bpy.types.Scene, prop.identifier)

    for cls in reversed(get_link_casted_classes()):
        bpy.utils.unregister_class(cls)
    # Unregister keymaps
    unregister_keymaps()
    unregister_frustum_properties()

    addon_updater_ops.unregister()