import bpy
from bpy.types import Panel

# -------------------------------------------------------------------
# MENUS
# -------------------------------------------------------------------

class VIEW3D_PT_LightingOps(Panel):
    bl_label = "Lighting Ops"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lighting"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("lighting.duplicate_light_cols", icon='DUPLICATE')
        col.operator("lighting.rename_light_cols", icon='OUTLINER_COLLECTION')
        col.operator("lighting.setup_light_linking", icon='LIGHT')
        col.separator()
        col.operator("lighting.modify_render_paths", icon='FILE_FOLDER')



# -------------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------------

def register():
    bpy.utils.register_class(VIEW3D_PT_LightingOps)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_LightingOps)