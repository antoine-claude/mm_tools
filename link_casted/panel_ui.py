# link_casted/panel_ui.py
import bpy
import os
from .core import match_shot, find_file

class VIEW3D_PT_link_casted(bpy.types.Panel):
    bl_label = "Link Casted"
    bl_idname = "VIEW3D_PT_link_casted_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Link Casted'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        candidates = find_file(match_shot())

        # Affiche les checkboxes if col already exist icon error
        link_col = layout.column()
        for path in candidates:
            basename = os.path.basename(path)
            prop_name = f"link_{basename.replace('.', '_')}"
            if hasattr(scene, prop_name):
                row = link_col.row()
                row.prop(scene, prop_name, text=basename.split(".")[0])
                # Add error icon if collection already exists
                if bpy.data.collections.get(basename.split(".")[0]):
                    row.label(icon='ERROR')

        op_row = layout.row()
        # Bouton pour charger les fichiers
        op_row.operator("linkcasted.load_files", text="Load Files")
        # Bouton pour linker les collections
        op_row.operator("linkcasted.link_collection", text="Link Checked Collections")
