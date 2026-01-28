from . import dependencies

dependencies.preload_modules()

import bpy
from .keymaps_and_menus import ( custom_file_menu_draw, register_keymaps, unregister_keymaps )
from .kitsu import (get_kitsu_classes,ensure_kitsu_handlers,remove_kitsu_handlers, register_kitsu_ui, register_kitsu_properties, unregister_kitsu_ui, unregister_kitsu_properties)
from . import (lighting, alert_path, anim_utils, toolbar_menu, frustum_vis, link_casted)
from . import addon_updater_ops
from . import updater_ui

bl_info = {
    "name": "MM Tools",
    "author": "Antoine C",
    "version": (0, 0, 8, 40),
}
classes = (
    updater_ui.DemoPreferences,
)
    
def register():
    addon_updater_ops.register(bl_info)

    for cls in classes:
        addon_updater_ops.make_annotations(cls)  # Avoid blender 2.8 warnings.
        bpy.utils.register_class(cls)
    # register lighting package (registers its UI and classes)
    lighting.register()
    alert_path.register()
    anim_utils.register()
    toolbar_menu.register()
    frustum_vis.register()
    link_casted.register()
    
    # Register all classes
    for cls_group in [ get_kitsu_classes()]:
        for cls in cls_group:
            bpy.utils.register_class(cls)
    
    # Register handlers
    ensure_kitsu_handlers()

    # bpy.types.TOPBAR_MT_editor_menus.append(register_kitsu_ui)
    bpy.types.TOPBAR_MT_file.draw = custom_file_menu_draw
    
    # Register keymaps and properties
    register_keymaps()
    register_kitsu_ui()
    register_kitsu_properties()

def unregister():
    # Unregister keymaps and properties first
    unregister_keymaps()

    # unregister lighting package
    lighting.unregister()
    alert_path.unregister()
    anim_utils.unregister()
    toolbar_menu.unregister()
    frustum_vis.unregister()
    link_casted.unregister()
    
    # Unregister UI
    # bpy.types.TOPBAR_MT_editor_menus.remove(register_kitsu_ui)
    if hasattr(bpy.types.TOPBAR_MT_file, "draw"):
        del bpy.types.TOPBAR_MT_file.draw

    
    # Unregister handlers
    remove_kitsu_handlers()
    unregister_kitsu_ui()
    unregister_kitsu_properties()
    
    # Unregister all classes in reverse order
    for cls_group in [get_kitsu_classes()]:
        for cls in reversed(cls_group):
            bpy.utils.unregister_class(cls)
    
    # Clean up dynamic properties
    for prop in list(bpy.types.Scene.bl_rna.properties):
        if prop.identifier.startswith("link_"):
            delattr(bpy.types.Scene, prop.identifier)


    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    addon_updater_ops.unregister()
