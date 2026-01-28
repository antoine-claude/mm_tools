# link_casted/ops.py
import bpy
import os
from .properties import update_scene_properties
from .core import find_file, match_shot, link_collection_matching_filename

class LINKCASTED_OT_load_files(bpy.types.Operator):
    bl_idname = "linkcasted.load_files"
    bl_label = "Load Files"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        update_scene_properties(scene)
        if context.area:
            context.area.tag_redraw()

        return {'FINISHED'}


class LINKCASTED_OT_link_collection(bpy.types.Operator):
    bl_idname = "linkcasted.link_asset_to_collection"
    bl_label = "Link Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        candidates = find_file(match_shot())
        
        for path in candidates:
            basename = os.path.basename(path).replace(".blend", "")
            prop_name = f"link_{basename}"

            if getattr(scene, prop_name, False):
                # Crée la collection parent si elle n'existe pas
                link_collection_matching_filename(path)

        return {'FINISHED'}
#register unregister property
classes = (LINKCASTED_OT_load_files, LINKCASTED_OT_link_collection)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        # Remove dynamic scene properties created by update_scene_properties (named like "link_<basename>")
        for attr in [a for a in dir(bpy.types.Scene) if a.startswith("link_")]:
            try:
                delattr(bpy.types.Scene, attr)
            except Exception:
                pass