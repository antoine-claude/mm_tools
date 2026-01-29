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
        link_props = [p for p in dir(scene) if p.startswith("link_")]

        if link_props:
            box = layout.box()

            groups = {"CHR": [], "PRP": [], "SET": [], "Camera": []}
            others = []

            for prop in link_props:
                parts = prop.split("_")
                if len(parts) > 2:
                    key = parts[2].upper()
                    prefix = key[:3]
                    if prefix in groups:
                        groups[prefix].append(prop)
                    else:
                        others.append(prop)
                else:
                    others.append(prop)

            # show uncategorized props first
            for prop in sorted(others):
                row = box.row()
                row.prop(scene, prop)

            # then show categorized props under their label
            for label in ("CHR", "PRP", "SET", "Camera"):
                items = groups[label]
                if items:
                    box.label(text=label)
                    for prop in sorted(items):
                        row = box.row()
                        row.prop(scene, prop)

        else:
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