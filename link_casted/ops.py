# link_casted/ops.py
import bpy
import os
from .properties import update_scene_properties
from .core import find_file, match_shot

class LINKCASTED_OT_load_files(bpy.types.Operator):
    bl_idname = "linkcasted.load_files"
    bl_label = "Load Files"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        update_scene_properties(scene)
        return {'FINISHED'}


class LINKCASTED_OT_link_collection(bpy.types.Operator):
    bl_idname = "linkcasted.link_collection"
    bl_label = "Link Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        candidates = find_file(match_shot())

        for path in candidates:
            basename = os.path.basename(path)
            prop_name = f"link_{basename.replace('.', '_')}"
            if hasattr(scene, prop_name) and getattr(scene, prop_name):
                # Crée la collection parent si elle n'existe pas
                new_col_name = f"Col_{basename.split('.')[0]}"
                if new_col_name not in bpy.data.collections:
                    new_col = bpy.data.collections.new(new_col_name)
                    context.scene.collection.children.link(new_col)
                else:
                    new_col = bpy.data.collections[new_col_name]

                # Link les collections du fichier .blend
                with bpy.data.libraries.load(path, link=True) as (data_from, data_to):
                    data_to.collections = data_from.collections

                for coll in data_to.collections:
                    if coll is not None:
                        new_col.children.link(coll)

        return {'FINISHED'}
