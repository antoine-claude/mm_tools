bl_info = {
    "name": "MM Menu",
    "version": (1, 0, 0),
}

import bpy
from . import ops
from .menu import VIEW3D_MT_MM
from .keymaps_and_menus import custom_file_menu_draw, register_keymaps, unregister_keymaps
from . import addon_updater_ops
@addon_updater_ops.make_annotations

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_MM")

def register():
    addon_updater_ops.register(bl_info)
    # Register operators from ops/
    for cls in ops.get_ops_classes():
        bpy.utils.register_class(cls)

    # Register menus
    bpy.utils.register_class(VIEW3D_MT_MM)
    bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    bpy.types.TOPBAR_MT_file.draw = custom_file_menu_draw

    # Register keymaps
    register_keymaps()

def unregister():
    # Unregister keymaps
    unregister_keymaps()

    # Unregister menus
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)
    if hasattr(bpy.types.TOPBAR_MT_file, "draw"):
        del bpy.types.TOPBAR_MT_file.draw
    bpy.utils.unregister_class(VIEW3D_MT_MM)

    # Unregister operators (in reverse)
    for cls in reversed(ops.get_ops_classes()):
        bpy.utils.unregister_class(cls)
