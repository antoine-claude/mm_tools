"""
Operators for build_shot addon
Provides operators for linking assets, refreshing cache, and saving
"""
import shutil

import bpy
import os
from bpy.types import Operator
from .. import cache, prefs
from .core import import_sound_strip, import_image_ref, init_modeling_scene_setup, init_rigging_scene_setup, set_shot_filepath, link_selected_assets, get_highest_version_file, get_audio_path, set_scene_settings, set_frames_timeline, get_sorted_task_types_for_shot
from ..types import (
    Shot,
    Department,
    TaskType
    )

# Individual asset link operator removed — selection handled via BoolProperties


class BUILD_SHOT_OT_link_selected_assets(Operator):
    """Link all assets for the selected shot"""
    bl_idname = "kitsu.link_selected_assets"
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
    bl_idname = "kitsu.add_asset_to_selection"
    bl_label = "Add Asset to Selection"
    bl_description = "Add the selected asset to the buildshot selection list"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        kitsu_scene = scene.kitsu
        asset_selected = scene.build_shot.asset_selected
        
        if not asset_selected:
            self.report({'ERROR'}, "Please select an asset first")
            return {'CANCELLED'}
        
        # Create a dynamic BoolProperty for this asset
        prop_name = f"buildshot_{asset_selected}"
        kitsu_scene_type = type(kitsu_scene)
        
        # Check if property already exists
        if hasattr(kitsu_scene, prop_name):
            setattr(kitsu_scene, prop_name, True)
            self.report({'INFO'}, f"Asset '{asset_selected}' already in selection (enabled)")
        else:
            try:
                # Create the dynamic property on the Kitsu scene property group.
                setattr(kitsu_scene_type, prop_name, bpy.props.BoolProperty(default=True))
                setattr(kitsu_scene, prop_name, True)
                self.report({'INFO'}, f"Asset '{asset_selected}' added to selection")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add asset: {str(e)}")
                return {'CANCELLED'}
        
        # Clear the asset_selected property
        scene.build_shot.asset_selected = ""
        
        return {'FINISHED'}

class BUILD_SHOT_OT_link_audio(Operator):
    """Link the audio file for the selected shot"""
    bl_idname = "kitsu.link_audio"
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

class BUILD_SHOT_OT_link_image_ref(Operator):
    """Link the image reference for the selected shot"""
    bl_idname = "kitsu.link_image_ref"
    bl_label = "Link Image Reference"
    bl_description = "Link the image reference for the selected shot"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        try:
            import_image_ref(context)
            self.report({'INFO'}, "Image reference linked successfully")
            return {'FINISHED'}
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error linking image reference: {str(e)}")
            return {'CANCELLED'}

class BUILD_SHOT_OT_remove_link_image_ref(Operator):
    """Remove the image reference for the selected shot"""
    bl_idname = "kitsu.remove_link_image_ref"
    bl_label = "Remove Image Reference"
    bl_description = "Remove the image reference for the selected shot"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        #If an image is in background camera, remove it
        try :
            if scene.camera and scene.camera.data.background_images:
                for img in scene.camera.data.background_images :
                    if img.image :
                        bpy.data.images.remove(img.image)
                        #remove background image slot
                        scene.camera.data.background_images.remove(img)
                self.report({'INFO'}, "Image reference removed successfully")
            else:
                self.report({'WARNING'}, "No image reference found to remove")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error removing image reference: {str(e)}")
            return {'CANCELLED'}

class BUILD_SHOT_OT_build_shot_layout(Operator):
    """Buld and save the current scene as a shot file"""
    bl_idname = "kitsu.build_shot_layout"
    bl_label = "Build Shot Layout"
    bl_description = "Save the current scene with the selected shot name"
    bl_options = {'REGISTER'}

    confirm_copy: bpy.props.BoolProperty(name="Confirm Copy", default=False)

    #Display task type in Layout and Animation Department
    previous_shot_task_type: bpy.props.EnumProperty(
        name="Source Task Type",
        items=cache.get_shot_task_types_enum)

    def execute(self, context):
        scene = context.scene
        selected_ep = cache.episode_active_get()
        selected_sequence = cache.sequence_active_get()
        selected_shot = cache.shot_active_get()
        department = cache.department_active_get()
        task_type = cache.task_type_department_active_get()
        # output_path = scene.build_shot.output_path
        
        if not selected_ep or selected_ep.name == "NONE":
            self.report({'ERROR'}, "Please select an episode")
            return {'CANCELLED'}
        
        if not selected_shot or selected_shot.name == "NONE":
            self.report({'ERROR'}, "Please select a shot")
            return {'CANCELLED'}
        
        # Use helper to get shot directory and filepath
        
        #If previous shot exist in sequence, duplicate file of prev_selected_shot uppper priority

        prod_dir = str(prefs.project_root_dir_get(context))
        filepath = set_shot_filepath(prod_dir, selected_ep.name, selected_sequence.name,
                        selected_shot.name, department.name, task_type.name
                        )
        
        if os.path.exists(filepath) :
            self.report({'ERROR'}, "This shot already exist")
            return {'CANCELLED'}
        
        #Look old shot
        all_shots = selected_sequence.get_all_shots()

        for i, shot in enumerate(all_shots):
            if shot.name == selected_shot.name and i > 0:
                # print("shot.name == selected_shot",shot.name)
                prev_shot = all_shots[i - 1]
                prev_shot_name = prev_shot.name
                break
        
        #Create file from last shot or from 0 
        if prev_shot_name and self.confirm_copy:

            prev_task_type = TaskType.by_id(self.previous_shot_task_type)
            prev_department = prev_task_type.get_department()

            prev_filepath = set_shot_filepath(
                prod_dir,
                selected_ep.name,
                selected_sequence.name,
                prev_shot_name,
                prev_department.name,
                prev_task_type.name,
            )

            if os.path.exists(prev_filepath):
                shutil.copy(prev_filepath, filepath)
            else:
                self.report({'WARNING'}, "Previous file not found, creating empty scene")
                self._create_empty_scene(context)

        else:
            self._create_empty_scene(context)


        #Set camera
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA' :
                bpy.data.scenes["Scene"].camera = obj
                break
        # Link sounds
        try:
            import_sound_strip(context)
            self.report({'INFO'}, "Audio linked successfully")
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
        import_image_ref(context)
        set_frames_timeline(context)
        #Set base settings for scene
        set_scene_settings(context)

        # `read_homefile()` can recreate Scene datablocks, so refresh the reference.
        scene = context.scene
        scene.render.filepath = scene.build_shot.output_path


        try:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
            print("filepath : " , filepath)
            self.report({'INFO'}, f"Shot saved: {filepath}")
            #Detect current context
            bpy.ops.kitsu.get_current_context()

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save shot: {str(e)}")
            return {'CANCELLED'}
        
    def invoke(self, context, event):
        # items = [("NONE", "None", "Create from scratch")]
        # items.append(cache.get_shot_task_types_enum_for_shot)

        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout

        layout.label(text="Create shot from:")
        layout.prop(self, "confirm_copy", text="Copy previous shot")
        if self.confirm_copy :
            layout.prop(self, "previous_shot_task_type", text="")

    def _create_empty_scene(self, context):

        bpy.ops.wm.read_homefile(app_template="")

        for collection in list(bpy.data.collections):
            bpy.data.collections.remove(collection)

        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj)

        try:            
            result = link_selected_assets(context)
            success_count = result['success_count']
            if success_count == 0:
                self.report({'ERROR'}, "Failed to link any assets")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to link assets: {str(e)}")
            return {'CANCELLED'}      

        # Link sounds
        try:
            #Remove sound strips linked from previous shot if exist
            for sequence in bpy.context.scene.sequence_editor.sequences:
                if sequence.type == 'SOUND':
                    bpy.context.scene.sequence_editor.sequences.remove(sequence)
            import_sound_strip(context)
            self.report({'INFO'}, "Audio linked successfully")
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
        
        set_frames_timeline(context)
        #Set base settings for scene
        set_scene_settings(context)

class BUILD_SHOT_OT_build_shot_animation(Operator):
    """Build and save the current scene as an animation shot file"""
    bl_idname = "kitsu.build_shot_animation"
    bl_label = "Build Shot Animation"
    bl_description = "Save the current scene with the selected shot name"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        selected_ep = context.scene.kitsu.episode_active_name
        selected_sequence = context.scene.kitsu.sequence_active_name
        selected_shot = context.scene.kitsu.shot_active_name
        department = scene.kitsu.department_active_name
        task_type = scene.kitsu.task_type_department_active_name
        
        if not selected_ep or selected_ep == "NONE":
            self.report({'ERROR'}, "Please select an episode")
            return {'CANCELLED'}
        
        if not selected_shot or selected_shot == "NONE":
            self.report({'ERROR'}, "Please select a shot")
            return {'CANCELLED'}
        
        if department != "Animation":
            self.report({'ERROR'}, "Animation folder type must be selected")
            return {'CANCELLED'}
        
        # Use helper to get shot directory and filepath
        prod_dir = str(prefs.project_root_dir_get(context))
        filepath = set_shot_filepath(prod_dir, selected_ep, selected_sequence, selected_shot, department, task_type)
        
        
        #Import sound strip
        if os.path.exists(get_audio_path(prod_dir, selected_ep, selected_shot)) :
            import_sound_strip(context)
        else :
            self.report({'WARNING'}, "No audio found for this shot")
        set_frames_timeline(context)
        #Set base settings for scene
        set_scene_settings(context)

        #Get previous department and task type to find source file for animation build
        previous_department = None
        previous_task_type = None
        shot = cache.shot_active_get()
        if shot:
            task_types = shot.get_all_task_types()
            task_types_sorted = sorted(task_types, key=lambda t: t.priority)
            for t in task_types_sorted:
                if t.name == task_type:
                    break
                previous_task_type = t
            
            if previous_task_type:
                previous_department = previous_task_type.get_department()
        if not previous_department or not previous_task_type:
            self.report({'ERROR'}, "No previous department/task type found for this shot")
            return {'CANCELLED'}
        
        source_filepath = get_highest_version_file(
            set_shot_filepath(prod_dir, selected_ep, selected_sequence, selected_shot, previous_department.name, previous_task_type.name)
            )
        
        if not source_filepath:
            self.report({'ERROR'}, "No source file found for animation build")
            return {'CANCELLED'}
        # copy source file to new filepath & open it
        try:
            shutil.copy2(source_filepath, filepath)
            self.report({'INFO'}, f"Shot saved: {filepath}")
            bpy.ops.wm.open_mainfile(filepath=filepath)              
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to build animation shot: {str(e)}")

class BUILD_SHOT_OT_get_current_context(Operator):
    """Get the current context from filepath and set active episode/sequence/shot in Kitsu props"""
    bl_idname = "kitsu.get_current_context"
    bl_label = "Get Current Context"
    bl_description = "Set active episode/sequence/shot in Kitsu props based on current file path"
    bl_options = {'REGISTER', 'UNDO'}

    _task_type = None   

    def execute(self, context):
        scene = context.scene
        current_filepath = bpy.data.filepath
        kitsu_props = context.scene.kitsu
        if not current_filepath:
            self.report({'ERROR'}, "Load a file first")
            return {'CANCELLED'}
        active_project = cache.project_active_get()
        basedir = os.path.dirname(current_filepath)
        basename = os.path.basename(current_filepath)
        filename = os.path.splitext(basename)[0]
        
        try:
            ep_name, seq_name, shot_name = filename.split("_")[1:4]
        except (ValueError, IndexError):
            self.report({'ERROR'}, "Filename format invalid. Expected: XX_EP_SEQ_SHOT_...")
            return {'CANCELLED'}
        
        # Set basic context from filename
        episode = active_project.get_episode_by_name(ep_name)
        if episode :
            kitsu_props.episode_active_name = episode.name
        scene.kitsu.episode_active_name = ep_name
        cache.episode_active_set_by_id(context, episode.id)
        sequence_name = f"{int(seq_name):04n}" 
        sequence = active_project.get_sequence_by_name(sequence_name, episode.id)
        if not sequence:
            self.report({"ERROR"}, f"Failed to find sequence: '{sequence.name}' on server")
            return {"CANCELLED"}

        kitsu_props.sequence_active_name = sequence.name
        cache.sequence_active_set_by_id(context, sequence.id)
        # Detect and load shot.
        shot = active_project.get_shot_by_name(sequence, shot_name)
        if not shot:
            self.report({"ERROR"}, f"Failed to find shot: '{shot_name}' on server")
            return {"CANCELLED"}

        kitsu_props.shot_active_name = shot.name
        cache.shot_active_set_by_id(context, shot.id)
        # Initialize department cache if needed
        # Get parent directory name (potential department folder)

        tasktype_dir_name = os.path.basename(basedir)
        department_dir_name = os.path.basename(os.path.dirname(basedir))

        shot = cache.shot_active_get()
        if not shot:
            self.report({'ERROR'}, "No active shot")
            return {'CANCELLED'}
        self._task_type = TaskType.by_name(tasktype_dir_name)
        
        # 4. Apply current task type
        if self._task_type:
            cache.task_type_department_active_set_by_id(
                context,
                self._task_type.id,
            )

            dept = self._task_type.get_department()

            if dept:
                scene.kitsu.department_active_name = dept.name
                cache.department_active_set_by_id(context, dept.id)
                scene.kitsu.task_type_department_active_name = self._task_type.name
                cache.task_type_department_active_set_by_id(context, self._task_type.id)
            
            #task_type_active_name set
            scene.kitsu.task_type_active_name = self._task_type.name
            cache.task_type_active_set_by_id(context, self._task_type.id)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "Task type not found")
            return {'CANCELLED'}

class BUILD_SHOT_OT_prev_shot(Operator):
    bl_idname = "kitsu.prev_shot"
    bl_label = "Previous Shot"

    def execute(self, context):

        seq = cache.sequence_active_get()
        current_shot = cache.shot_active_get()

        if not seq or not current_shot:
            return {'CANCELLED'}

        shots = seq.get_all_shots()

        for i, shot in enumerate(shots):
            if shot.id == current_shot.id and i > 0:
                prev_shot = shots[i - 1]

                context.scene.kitsu.shot_active_name = prev_shot.name
                cache.shot_active_set_by_id(context, prev_shot.id)
                return {'FINISHED'}

        return {'CANCELLED'}  

class BUILD_SHOT_OT_next_shot(Operator):
    bl_idname = "kitsu.next_shot"
    bl_label = "Next Shot"

    def execute(self, context):

        seq = cache.sequence_active_get()
        current_shot = cache.shot_active_get()

        if not seq or not current_shot:
            return {'CANCELLED'}

        shots = seq.get_all_shots()

        for i, shot in enumerate(shots):
            if shot.id == current_shot.id and i < len(shots) - 1:
                next_shot = shots[i + 1]

                context.scene.kitsu.shot_active_name = next_shot.name
                cache.shot_active_set_by_id(context, next_shot.id)
                return {'FINISHED'}

        return {'CANCELLED'}

class BUILD_SHOT_OT_prev_task_type(Operator):
    bl_idname = "kitsu.prev_task_type"
    bl_label = "Previous Task Type"

    def execute(self, context):

        shot = cache.shot_active_get()
        current = cache.task_type_department_active_get()

        if not shot or not current:
            return {'CANCELLED'}

        task_types = get_sorted_task_types_for_shot(shot)

        for i, t in enumerate(task_types):
            if t.id == current.id and i > 0:
                prev = task_types[i - 1]

                self._apply(context, prev)
                return {'FINISHED'}

        return {'CANCELLED'}

    def _apply(self, context, task_type):

        dept = task_type.get_department()

        if dept:
            context.scene.kitsu.department_active_name = dept.name
            cache.department_active_set_by_id(context, dept.id)
        context.scene.kitsu.task_type_department_active_name = task_type.name
        cache.task_type_department_active_set_by_id(context, task_type.id)

class BUILD_SHOT_OT_next_task_type(Operator):
    bl_idname = "kitsu.next_task_type"
    bl_label = "Next Task Type"

    def execute(self, context):

        shot = cache.shot_active_get()
        current = cache.task_type_department_active_get()

        if not shot or not current:
            return {'CANCELLED'}

        task_types = get_sorted_task_types_for_shot(shot)

        for i, t in enumerate(task_types):
            if t.id == current.id and i < len(task_types) - 1:
                nxt = task_types[i + 1]

                self._apply(context, nxt)
                return {'FINISHED'}

        return {'CANCELLED'}

    def _apply(self, context, task_type):

        dept = task_type.get_department()

        if dept:
            context.scene.kitsu.department_active_name = dept.name
            cache.department_active_set_by_id(context, dept.id)
        context.scene.kitsu.task_type_department_active_name = task_type.name
        cache.task_type_department_active_set_by_id(context, task_type.id)


"""
Operator Build Assets Task type(Model, Shading, Rigging)
"""

class BUILD_ASSETS_OT_build(Operator):
    bl_idname = "kitsu.build_assets"
    bl_label = "Build Assets"

    def execute(self, context):
        #Initialize scene for asset
        asset_active = cache.asset_active_get()
        task_type_active = cache.task_type_active_get()
        #check if asset not already build in folder
        asset_dir = prefs.asset_dir_get(context)
        asset_folder_path = os.path.join(asset_dir, asset_active.name, task_type_active.name)
        asset_file_name = f"{asset_active.name}_{task_type_active.short_name}.blend"
        asset_file_path = os.path.join(asset_folder_path, asset_file_name)
        if os.path.exists(asset_file_path):
            self.report({'ERROR'}, f"Asset file already exists: {asset_file_path}")
            return {'CANCELLED'}
        #Create file from general new file
        bpy.ops.wm.read_homefile(app_template="")
        #Clean scene
        for collection in list(bpy.data.collections):
            bpy.data.collections.remove(collection)
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj)
        
        #Create collection
        asset_task_type_collection_name = f"{asset_active.name}_{task_type_active.name}"
        #check if collection already exist in scene
        if not asset_active.name in bpy.data.collections:
            asset_collection = bpy.data.collections.new(asset_active.name)
        else :
            asset_collection = bpy.data.collections[asset_active.name]
        asset_task_type_collection = bpy.data.collections.new(asset_task_type_collection_name)

        bpy.context.scene.collection.children.link(asset_collection)
        asset_collection.children.link(asset_task_type_collection)

        init_modeling_scene_setup(context)
        init_rigging_scene_setup(asset_active)

classes = (
    BUILD_SHOT_OT_link_selected_assets,
    BUILD_SHOT_OT_add_asset_to_selection,
    BUILD_SHOT_OT_build_shot_layout,
    BUILD_SHOT_OT_build_shot_animation,
    BUILD_SHOT_OT_link_audio,
    BUILD_SHOT_OT_link_image_ref,
    BUILD_SHOT_OT_remove_link_image_ref,
    BUILD_SHOT_OT_get_current_context,
    BUILD_SHOT_OT_prev_task_type,
    BUILD_SHOT_OT_next_task_type,
    BUILD_SHOT_OT_prev_shot,
    BUILD_SHOT_OT_next_shot,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
