# link_casted/panel_ui.py
import bpy

class VIEW3D_PT_link_casted(bpy.types.Panel):
    bl_label = "Link Casted"
    bl_idname = "LINKCASTED_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LinkCasted'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if any(prop.startswith("link_") for prop in dir(scene)):
            box = layout.box()
            for prop in dir(scene):
                if prop.startswith("link_"):
                    row = box.row()
                    row.prop(scene, prop)


        else :
            layout.label(text="Pas d'assets trouvés.")
        layout.operator("linkcasted.load_files", icon="FILE_REFRESH")
        layout.operator("linkcasted.link_asset_to_collection", icon="FILE_REFRESH")


classes = (VIEW3D_PT_link_casted,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)