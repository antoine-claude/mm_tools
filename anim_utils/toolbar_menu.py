import bpy


class VIEW3D_MT_MM(bpy.types.Menu):
    bl_label = "MM"
    bl_idname = "VIEW3D_MT_MM"

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.mm_libraries_remapper", icon='LIBRARY_DATA_DIRECT')
        layout.operator("view3d.mm_bake_pas2", icon='ARMATURE_DATA')
        layout.operator("view3d.mm_append_previous_frame", icon='PLAY_REVERSE')
        layout.separator()

def custom_file_mm_menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_MM")

# -------------------------------------------------------------------
# REGISTER

classes = (VIEW3D_MT_MM,)
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_editor_menus.append(custom_file_mm_menu_draw)    
    # TOPBAR draw assignment moved to package `__init__.py` to centralize menu hooks
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_editor_menus.remove(custom_file_mm_menu_draw)
    # TOPBAR draw cleanup handled by package `__init__.py`
