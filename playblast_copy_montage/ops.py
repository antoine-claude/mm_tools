import bpy
import os
import shutil
import sys
import subprocess
from .utils import get_playblast_dest_file, remap_output_path, get_playblast_source_file



class PLAYBLAST_OT_remap_output_path(bpy.types.Operator):
    bl_idname = "playblast.remap_output_path"
    bl_label = "Remap le Outputpath"
    bl_description = "Change le outputpath par rapport à l'emplacement du fichier et son nom"
    def execute(self, context):
        scene = context.scene
        remap_path = remap_output_path(scene)
        if not remap_path:
            self.report({'ERROR'}, "[ALERT] le fichier n'est ni dans Layout, Animation_Spline ou Animation_Stopmo, pas de nouveau outputpath")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Le chemin outputpath : {remap_path}")
        return {'FINISHED'}

class PLAYBLAST_OT_duplicate_ffmpeg(bpy.types.Operator):
    bl_idname = "playblast.duplicate_ffmpeg"
    bl_label = "Dupliquer le playblast"
    bl_description = "Copie le fichier playblast FFmpeg vers le chemin indiqué"

    def execute(self, context):
        scene = context.scene

        source_file = get_playblast_source_file(scene)
        if not source_file:
            self.report({'ERROR'}, "Le playblast n'existe pas encore.")
            return {'CANCELLED'}

        if not os.path.isdir(bpy.path.abspath(scene.copy_output.copy_output_path)):
            self.report({'ERROR'}, "Chemin de destination invalide")
            return {'CANCELLED'}

        dest_file = get_playblast_dest_file(scene)
        dest_dir = os.path.dirname(dest_file)
        
        if dest_file :
            os.makedirs(dest_dir, exist_ok=True)

            try:
                shutil.copy2(source_file, dest_file)
            except Exception as e:
                self.report({'ERROR'}, str(e))
                return {'CANCELLED'}

            self.report({'INFO'}, f"Copié vers : {dest_file}")
            return {'FINISHED'}

class WM_OT_open_copy_output_path(bpy.types.Operator):
    bl_idname = "wm.open_copy_output_path"
    bl_label = "Ouvrir le dossier Livraison"
    bl_description = "Ouvre le dossier défini dans Chemin de destination"

    def execute(self, context):
        # Build the destination dir to open (same logic as the duplicator)
        base_dest = bpy.path.abspath(context.scene.copy_output.copy_output_path)
        blend_name = bpy.path.basename(bpy.data.filepath)
        parts = blend_name.split("_")
        ep = parts[1] if len(parts) > 1 else "UNKNOWN"
        layer = context.scene.copy_output.copy_output_layer
        path = os.path.join(base_dest, ep, f"EP{ep}_{layer}")
        if not os.path.isdir(path):
            self.report({'ERROR'}, "Chemin invalide")
            return {'CANCELLED'}
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (PLAYBLAST_OT_remap_output_path,
           PLAYBLAST_OT_duplicate_ffmpeg,
           WM_OT_open_copy_output_path,
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
