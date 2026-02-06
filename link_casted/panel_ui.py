# link_casted/panel_ui.py
import bpy
from .cache import get_cached

class VIEW3D_PT_link_casted(bpy.types.Panel):
    bl_label = "Link Casted"
    bl_idname = "LINKCASTED_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LinkCasted'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cached = get_cached()
        if cached.get("has_props"):
            box = layout.box()

            # show uncategorized props first
            for prop in cached.get("others", []):
                row = box.row()
                row.prop(scene, prop)

            # show categorized props under their label
            for label in ("CHR", "PRP", "SET", "CAMERA"):
                items = cached.get("groups", {}).get(label, [])
                if items:
                    box.label(text=label)
                    for prop in items:
                        row = box.row()
                        row.prop(scene, prop)

        else:
            layout.label(text="Pas d'assets trouvés.")
        layout.operator("linkcasted.load_files", icon="FILE_REFRESH")
        layout.operator("linkcasted.link_asset_to_collection", icon="FILE_REFRESH")
        layout.operator("linkcasted.unlink_asset_to_collection", icon="FILE_REFRESH")
        layout.operator("linkcasted.link_sounds", icon="SOUND")


classes = (VIEW3D_PT_link_casted,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)