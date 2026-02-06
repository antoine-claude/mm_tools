import bpy
import os
from .utils import find_new_shot, parsed_filepath, increment_number
from bpy.props import StringProperty, BoolProperty


class BUILD_ANIME_OT_CreateAnimationFolders(bpy.types.Operator):
    bl_idname = "animation.create_folders"
    bl_label = "Generate Animations folders"
    bl_description = "Crée les dossiers Animation_Block, Animation_Spline et Animation_Stopmo"

    def execute(self, context):
        base_path = os.path.dirname(os.path.dirname(bpy.data.filepath))
        if not base_path:
            self.report({'ERROR'}, "Enregistrez d'abord votre fichier .blend")
            return {'CANCELLED'}

        folders = ["Animation_Block", "Animation_Spline", "Animation_Stopmo"]
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.report({'INFO'}, f"Dossier créé : {folder_path}")
            else:
                self.report({'INFO'}, f"Dossier déjà existant : {folder_path}")

        return {'FINISHED'}

class BUILD_ANIME_OT_CreateBlockingFile(bpy.types.Operator):
    bl_idname = "animation.create_blocking_file"
    bl_label = "Generate Blocking file from Layout"
    bl_description = "Crée un fichier Blocking.blend dans Animation_Block"

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Enregistrez d'abord votre fichier .blend")
            return {'CANCELLED'}
        lay_path = os.path.basename(os.path.dirname(filepath)) 
        if lay_path == "Layout" :
            base_path = os.path.dirname(os.path.dirname(bpy.data.filepath))
        else:
            self.report({'ERROR'}, "Le fichier doit être dans un dossier 'Layout'")
            return {'CANCELLED'}
        
        # base_path = os.path.dirname(os.path.dirname(os.path.dirname(filepath)))
        anim_path = os.path.join(base_path, "Animation")
        block_path = os.path.join(anim_path, "Animation_Block")
        spline_path = os.path.join(anim_path, "Animation_Spline")
        stopmo_path = os.path.join(anim_path, "Animation_Stopmo")
        if not os.path.exists(block_path):
            os.makedirs(block_path)
        if not os.path.exists(spline_path):
            os.makedirs(spline_path)
        if not os.path.exists(stopmo_path):
            os.makedirs(stopmo_path)

        file_path = os.path.join(block_path, increment_number(parsed_filepath(filepath), layout=True))
        print(file_path)
        if not os.path.exists(file_path):
            bpy.ops.wm.save_as_mainfile(filepath=file_path)
            self.report({'INFO'}, f"Fichier créé : {file_path}")
        else:
            self.report({'INFO'}, f"Fichier déjà existant : {file_path}")

        return {'FINISHED'}

class BUILD_ANIME_OT_CreateAnimeNextStep(bpy.types.Operator):
    bl_idname = "animation.create_anime_next_step"
    bl_label = "Generate next animation step file"
    bl_description = "Crée un fichier Spline.blend dans Animation_Spline"

    def execute(self, context):
        filepath = bpy.data.filepath
        if os.path.basename(os.path.dirname(filepath)) == "Animation_Stopmo":
            self.report({'ERROR'}, "Ne marche que pour créer Spline et Stopmo.")
            return {'CANCELLED'}
        if os.path.basename(os.path.dirname(filepath)) == "Animation_Block":
            folder = "Animation_Spline"
        if os.path.basename(os.path.dirname(filepath)) == "Animation_Spline":
            folder = "Animation_Stopmo"      
        if os.path.basename(os.path.dirname(filepath)) == "Animation_Stopmo":
            self.report({'ERROR'}, "Ne marche que pour créer Spline et Stopmo.")
            return {'CANCELLED'}
        base_path = os.path.dirname(os.path.dirname(filepath))
        if not base_path:
            self.report({'ERROR'}, "Enregistrez d'abord votre fichier .blend")
            return {'CANCELLED'}

        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, increment_number(parsed_filepath(filepath)))
        print(file_path)
        if not os.path.exists(file_path):
            bpy.ops.wm.save_as_mainfile(filepath=file_path)
            self.report({'INFO'}, f"Fichier créé : {file_path}")
        else:
            self.report({'INFO'}, f"Fichier déjà existant : {file_path}")

        return {'FINISHED'}


class BUILD_LAYOUT_OT_BuldNextShot(bpy.types.Operator):
    bl_idname = "layout.build_next_layout_shot"
    bl_label = "Generate Next Layout Shot"
    bl_description = "Crée les despuis le fichier ouvert le shot suivant"

    def execute(self, context):
        blend_path = bpy.data.filepath
        if not blend_path :
            self.report({'ERROR'}, "No file path defined.")
            return {'CANCELLED'}
        else :
            new_shot_path = find_new_shot(blend_path)
            if not new_shot_path:
                self.report({'ERROR'}, "Next shot folder not found or could not be created.")
                return {'CANCELLED'}
            try:
                bpy.ops.wm.save_as_mainfile(filepath=new_shot_path)
            except Exception as e:
                self.report({'ERROR'}, f"Save failed: {e}")
                return {'CANCELLED'}
            bpy.ops.wm.open_next_shot_confirm('INVOKE_DEFAULT', filepath=new_shot_path)
        return {'FINISHED'}

class WM_OT_OpenNextShotConfirm(bpy.types.Operator):
    bl_idname = "wm.open_next_shot_confirm"
    bl_label = "Do you want to open next shot?"

    filepath: StringProperty()
    load_ui: BoolProperty(name="Load UI", default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Open next shot file:")
        if self.filepath is not None :
            layout.label(text=self.filepath)
        layout.prop(self, "load_ui", text="Load UI")

    def execute(self, context):
        if self.filepath and os.path.exists(self.filepath):
            bpy.ops.wm.open_mainfile(filepath=self.filepath, load_ui=self.load_ui)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}


classes = (BUILD_ANIME_OT_CreateAnimationFolders,
           BUILD_ANIME_OT_CreateBlockingFile,
           BUILD_ANIME_OT_CreateAnimeNextStep,
           BUILD_LAYOUT_OT_BuldNextShot,
           WM_OT_OpenNextShotConfirm,
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
