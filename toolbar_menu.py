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
