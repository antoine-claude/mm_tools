"""
Operators for build_shot addon
Provides operators for linking assets, refreshing cache, and saving
"""

import shutil

import bpy
import os
from bpy.types import Operator
from .. import cache, prefs
from .core import import_sound_strip, get_shot_dir, set_shot_filepath, link_selected_assets, get_highest_version_file, get_audio_path, set_scene_settings, set_frames_timeline


# Individual asset link operator removed — selection handled via BoolProperties


class BUILD_SHOT_OT_link_selected_assets(Operator):
    """Link all assets for the selected shot"""
    bl_idname = "build_shot.link_selected_assets"
    bl_label = "Link Selected Assets"
    bl_description = "Link all selected assets from the selected shot"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        prod_dir = str(prefs.project_root_dir_get(context))
            
        try:
            result = link_selected_assets(context)
            success_count = result['success_count']
            failed_assets = result['failed_assets']
            if success_count > 0:
                msg = f"Linked {success_count} assets"
                if failed_assets:
                    msg += f", failed to link: {', '.join(failed_assets[:3])}"
                    if len(failed_assets) > 3:
                        msg += f" and {len(failed_assets) - 3} more"
                self.report({'INFO'}, msg)
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to link any assets")
                return {'CANCELLED'}
        
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error linking assets: {str(e)}")
            return {'CANCELLED'}


class BUILD_SHOT_OT_add_asset_to_selection(Operator):
    """Add the selected asset to buildshot selection"""
    bl_idname = "build_shot.add_asset_to_selection"
    bl_label = "Add Asset to Selection"
    bl_description = "Add the selected asset to the buildshot selection list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        asset_selected = scene.build_shot.asset_selected
        
        if not asset_selected:
            self.report({'ERROR'}, "Please select an asset first")
            return {'CANCELLED'}
        
        # Create a dynamic BoolProperty for this asset
        prop_name = f"buildshot_{asset_selected}"
        
        # Check if property already exists
        if hasattr(scene, prop_name):
            setattr(scene, prop_name, True)
            self.report({'INFO'}, f"Asset '{asset_selected}' already in selection (enabled)")
        else:
            try:
                # Create the dynamic property on the scene
                bpy.types.Scene.buildshot_temp = bpy.props.BoolProperty(default=True)
                setattr(bpy.types.Scene, prop_name, bpy.props.BoolProperty(default=True))
                setattr(scene, prop_name, True)
                delattr(bpy.types.Scene, "buildshot_temp")
                self.report({'INFO'}, f"Asset '{asset_selected}' added to selection")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add asset: {str(e)}")
                return {'CANCELLED'}
        
        # Clear the asset_selected property
        scene.build_shot.asset_selected = ""
        
        return {'FINISHED'}

class BUILD_SHOT_OT_link_audio(Operator):
    """Link the audio file for the selected shot"""
    bl_idname = "build_shot.link_audio"
    bl_label = "Link Audio"
    bl_description = "Link the audio file for the selected shot"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        try:
            import_sound_strip(context)
            self.report({'INFO'}, "Audio linked successfully")
            return {'FINISHED'}
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error linking audio: {str(e)}")
            return {'CANCELLED'}


class BUILD_SHOT_OT_build_shot_layout(Operator):
    """Buld and save the current scene as a shot file"""
    bl_idname = "build_shot.build_shot_layout"
    bl_label = "Build Shot Layout"
    bl_description = "Save the current scene with the selected shot name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        selected_ep = cache.episode_active_get().name
        selected_sequence = cache.sequence_active_get().name
        selected_shot = cache.shot_active_get().name
        type_folder = scene.build_shot.type_folder
        anim_sub_folder = scene.build_shot.anim_sub_folder
        # output_path = scene.build_shot.output_path
        
        if not selected_ep or selected_ep == "NONE":
            self.report({'ERROR'}, "Please select an episode")
            return {'CANCELLED'}
        
        if not selected_shot or selected_shot == "NONE":
            self.report({'ERROR'}, "Please select a shot")
            return {'CANCELLED'}
        
        # Use helper to get shot directory and filepath
        
        prod_dir = str(prefs.project_root_dir_get(context))
        shot_dir = get_shot_dir(prod_dir, selected_ep, selected_sequence, selected_shot, type_folder, anim_sub_folder)
        filepath = set_shot_filepath(prod_dir, selected_ep, selected_sequence, selected_shot, type_folder, anim_sub_folder)
        
        if os.path.exists(filepath) :
            self.report({'ERROR'}, "This shot already exist")
            return {'CANCELLED'}
        
        # Create directory if it doesn't exist
        os.makedirs(shot_dir, exist_ok=True)
        
        # Link assets before saving
        try:
            bpy.ops.wm.read_homefile(app_template="") 
            for collection in bpy.data.collections:
                bpy.data.collections.remove(collection)
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
            
            result = link_selected_assets(context)
            success_count = result['success_count']
            if success_count == 0:
                self.report({'ERROR'}, "Failed to link any assets")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to link assets: {str(e)}")
            return {'CANCELLED'}
        
        print("filepath : " , filepath)
        # Link sounds
        try:
            import_sound_strip(context)
            self.report({'INFO'}, "Audio linked successfully")
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
        
        set_frames_timeline(context)
        #Set base settings for scene
        set_scene_settings(context)


        try:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
            print("filepath : " , filepath)
            self.report({'INFO'}, f"Shot saved: {filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save shot: {str(e)}")
            return {'CANCELLED'}

class BUILD_SHOT_OT_build_shot_animation(Operator):
    """Build and save the current scene as an animation shot file"""
    bl_idname = "build_shot.build_shot_animation"
    bl_label = "Build Shot Animation"
    bl_description = "Save the current scene with the selected shot name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        selected_ep = context.scene.kitsu.episode_active_name
        selected_sequence = context.scene.kitsu.sequence_active_name
        selected_shot = context.scene.kitsu.shot_active_name
        type_folder = scene.build_shot.type_folder
        anim_sub_folder = scene.build_shot.anim_sub_folder
        
        if not selected_ep or selected_ep == "NONE":
            self.report({'ERROR'}, "Please select an episode")
            return {'CANCELLED'}
        
        if not selected_shot or selected_shot == "NONE":
            self.report({'ERROR'}, "Please select a shot")
            return {'CANCELLED'}
        
        if type_folder != "Animation":
            self.report({'ERROR'}, "Animation folder type must be selected")
            return {'CANCELLED'}
        
        # Use helper to get shot directory and filepath
        prod_dir = str(prefs.project_root_dir_get(context))
        shot_dir = get_shot_dir(prod_dir, selected_ep, selected_sequence, selected_shot, type_folder, anim_sub_folder)
        filepath = set_shot_filepath(prod_dir, selected_ep, selected_sequence, selected_shot, type_folder, anim_sub_folder)
        
        # Define animation source mapping
        anim_source_map = {
            "Animation_Blocking": ("Layout", None, "Layout shot must be built first"),
            "Animation_Spline": ("Animation", "Animation_Blocking", "Blocking shot must be built first"),
            "Animation_Stopmo": ("Animation", "Animation_Spline", "Spline shot must be built first"),
        }
        
        #Import sound strip
        if os.path.exists(get_audio_path(prod_dir, selected_ep, selected_shot)) :
            import_sound_strip(context)
        else :
            self.report({'WARNING'}, "No audio found for this shot")
        set_frames_timeline(context)
        #Set base settings for scene
        set_scene_settings(context)

        if anim_sub_folder in anim_source_map:
            source_type, source_sub, error_msg = anim_source_map[anim_sub_folder]
            source_filepath = set_shot_filepath(prod_dir, selected_ep, selected_sequence, selected_shot, source_type, source_sub)
            source_filepath = get_highest_version_file(source_filepath)
            
            if not source_filepath or not os.path.exists(source_filepath):
                self.report({'ERROR'}, error_msg)
                return {'CANCELLED'}
            
            os.makedirs(shot_dir, exist_ok=True)
            shutil.copy(source_filepath, filepath)
            self.report({'INFO'}, f"Shot saved: {filepath}")
            bpy.ops.wm.open_mainfile(filepath=filepath)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Invalid animation subfolder: {anim_sub_folder}")
            return {'CANCELLED'}


#Operator for set kitsu.shot_active_name to the current shot name and save the file
class BUILD_SHOT_OT_get_current_context(Operator):
    """Get the current context from filepath and set active episode/sequence/shot in Kitsu props"""
    bl_idname = "build_shot.get_current_context"
    bl_label = "Get Current Context"
    bl_description = "Set active episode/sequence/shot in Kitsu props based on current file path"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        current_filepath = bpy.data.filepath
        
        if not current_filepath:
            self.report({'ERROR'}, "Load a file first")
            return {'CANCELLED'}
        
        basedir = os.path.dirname(current_filepath)
        basename = os.path.basename(current_filepath)
        filename = os.path.splitext(basename)[0]
        ep_name, seq_name, shot_name = filename.split("_")[1:4]
        

        scene.kitsu.episode_active_name = ep_name
        scene.kitsu.sequence_active_name = f"{int(seq_name):04d}"
        scene.kitsu.shot_active_name = shot_name
        scene.build_shot.type_folder = "Animation"
        # print("type folder ", os.path.basename(os.path.dirname(basedir)))
        # print("anim sub folder ", os.path.basename(basedir))
        if os.path.basename(os.path.dirname(basedir)) == "Animation" :
            if os.path.basename(basedir) in ["Animation_Blocking", "Animation_Spline", "Animation_Stopmo"]:
                # Set next animation sub folder based on current folder
                if os.path.basename(basedir) == "Animation_Blocking":
                    scene.build_shot.anim_sub_folder = "Animation_Spline"
                elif os.path.basename(basedir) == "Animation_Spline":
                    scene.build_shot.anim_sub_folder = "Animation_Stopmo"
                elif os.path.basename(basedir) == "Animation_Stopmo":
                    scene.build_shot.anim_sub_folder = "Animation_Stopmo"

        elif os.path.basename(basedir) == "Layout":
            scene.build_shot.anim_sub_folder = "Animation_Blocking"
                

        return {'FINISHED'}
    


classes = (
    BUILD_SHOT_OT_link_selected_assets,
    BUILD_SHOT_OT_add_asset_to_selection,
    BUILD_SHOT_OT_build_shot_layout,
    BUILD_SHOT_OT_build_shot_animation,
    BUILD_SHOT_OT_link_audio,
    BUILD_SHOT_OT_get_current_context,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
