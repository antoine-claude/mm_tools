import re

import bpy
import os
from .. import cache, bkglobals, prefs
from ..context import core as context_core
from pathlib import Path
import shutil
# Category values are defined in enum props.py KITSU_property_group_scene under category
def is_edit_context():
    return bpy.context.scene.kitsu.category == "EDIT"


def is_sequence_context():
    return bpy.context.scene.kitsu.category == "SEQ"


def is_asset_context():
    return bpy.context.scene.kitsu.category == "ASSET"


def is_shot_context():
    return bpy.context.scene.kitsu.category == "SHOT"


def draw_department_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw output layer selection (department and animation task_type)"""
    layout.label(text="Department :")
    row = layout.row(align=True)
    row.prop(context.scene.build_shot, "department_active_name")

def draw_output_task_type_department_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw task type for department selector, only if department is set to Animation"""
    if cache.department_active_get().name == "Animation":
        row = layout.row(align=True)
        row.prop(context.scene.kitsu, "task_type_department_active_name")

def draw_asset_filter_and_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw asset type selector, asset scope, and asset selection in split row"""
    # Asset type selector - from global kitsu context (kitsu.asset_type_active_name)
    layout.label(text="Add Asset out of casting : ")
    box = layout.box()
    split_scope = box.split(factor=1.0)
    split_scope.prop(context.scene.build_shot, "asset_scope", text="Scope")
    box.prop(context.scene.kitsu, "asset_type_active_name", text="Asset Type")
    
    # Asset scope selector
    
    # Asset selection with scope
    split_select = box.split(factor=1.0)
    split_select.prop(context.scene.build_shot, "asset_selected", text="Select Asset")
    
    # Add button to add selected asset to buildshot selection
    row_add = box.row(align=True)
    row_add.operator(
        "kitsu.add_asset_to_selection",
        text="Add to Selection",
        icon='ADD'
    )

def draw_build_shot_section(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw build shot output path and build button"""
    layout.separator()
    shot_active = cache.shot_active_get()
    if not shot_active or not shot_active.id:
        return
    if not context.scene.kitsu.department_active_name:
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Select a department", icon="INFO")
        return

    department = cache.department_active_get()

    # if not department or not department.id:
    #     print("No active department")
    # else:
    task_types = cache.get_all_task_types_for_department(department)

    if task_types is None:
        row = layout.row(align=True)
        row.label(text="Select a task Type")
        return
            
    # if not context.scene.kitsu.task_type_department_active_name :
    #     row = layout.row(align=True)
    #     row.label(text="Select a task Type")
    #     return
    
    output_path = get_new_output_path(context)
    highest_version = get_highest_version_file(output_path)
    if not highest_version:
        if not os.path.exists(os.path.dirname(output_path)):
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text=f"Folder {context.scene.kitsu.department_active_name} missing",
                       icon="ERROR")
            return
        # Build shot button - conditional based on type_folder
        if context.scene.kitsu.department_active_name == "Animation":
            layout.operator(
                "kitsu.build_shot_animation",
                text="Build Animation Shot",
                icon='FILE_TICK'
            )
        else:
            layout.operator(
                "kitsu.build_shot_layout",
                text="Build Layout Shot",
                icon='FILE_TICK'
            )
        layout.label(text=f"{output_path}")


    elif highest_version and os.path.exists(highest_version):
        if bpy.data.filepath == highest_version:
            layout.label(text=f"Actual File",icon="CHECKMARK")
        else :
            #Open existing file button
            open_file = layout.operator(
                "wm.open_mainfile",
                text="Open Existing Shot",
                icon='FILE_FOLDER'
            )
            open_file.filepath = highest_version
            open_file.load_ui = False
            open_file.display_file_selector = False

            layout.label(text=f"Shot already built: {highest_version}",
                        icon="CHECKMARK")


def draw_assets_for_shot(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw assets available for the selected shot plus any manually-added assets"""
    scene = context.scene
    kitsu_scene = scene.kitsu
    asset_dir = prefs.asset_dir_get(context)
    shot_active = cache.shot_active_get()
    
    if not shot_active or not shot_active.id:
        layout.label(text="Select a shot first", icon='INFO')
        return
    
    # Get assets for the selected shot
    try:
        shot_assets = shot_active.get_all_assets()
    except Exception:
        layout.label(text="Unable to load assets", icon='ERROR')
        return
    
    # Get any manually-added assets (buildshot_ properties that aren't in shot)
    shot_asset_names = {a.name for a in shot_assets}
    manually_added = []
    for attr_name in dir(kitsu_scene):
        if attr_name.startswith("buildshot_"):
            asset_name = attr_name.replace("buildshot_", "")
            if asset_name not in shot_asset_names and hasattr(kitsu_scene, attr_name):
                manually_added.append(asset_name)
    
    if not shot_assets and not manually_added:
        layout.label(text="No assets found for this shot", icon='INFO')
        return
    
    # Display assets in a box
    box = layout.box()
    
    # Display shot assets organized by type
    if shot_assets:
        box.label(text="Shot Assets : ", icon="PACKAGE")
        for label in ("CHR", "PRP", "SET", "ITM", "FX", "CAMERA"):
            # items = [a for a in shot_assets if f"_{label}" in a.name or (label == "CAMERA" and a.name == "MM_Camera")]
            items = []
            for a in shot_assets:
                parts = a.name.split("_")
                is_fx = len(parts) > 2 and parts[2].startswith("FX")

                if label == "FX" and is_fx:
                    items.append(a)
                elif label != "FX" and f"_{label}" in a.name and not is_fx:
                    items.append(a)
                elif label == "CAMERA" and a.name == "MM_Camera":
                    items.append(a)
            if items:
                box.label(text=f"{label} :")
                for asset in items:
                    # Set icon based on category
                    if asset.name == "MM_Camera":
                        icon = 'VIEW_CAMERA'
                    elif label == 'CHR':
                        icon = 'OUTLINER_OB_ARMATURE'
                    elif label == 'PRP':
                        icon = 'ASSET_MANAGER'
                    elif label == 'SET':
                        icon = 'HOME'
                    elif label == 'ITM':
                        icon = 'MESH_CUBE'
                    elif label == 'FX':
                        icon = 'SHADERFX'
                    else:
                        icon = 'PACKAGE'
                    asset_row = box.row(align=True)
                    asset_row.use_property_split = False
                    asset_row.alignment = 'LEFT'
                    prop_name = f"buildshot_{asset.name}"
                    if hasattr(kitsu_scene, prop_name):
                        asset_row.prop(kitsu_scene, prop_name, text="")
                    asset_row.label(text=asset.name, icon=icon)
                    
                    # Check if asset file exists
                    asset_path = get_asset_path(asset.name, asset_dir)
                    # print('asset_path ::', asset.name,asset_path)
                    if not asset_path or not os.path.exists(asset_path):
                        asset_row.label(text="File missing", icon="ERROR")
    
    # Display manually-added assets section
    if manually_added:
        box.separator()
        box.label(text="Added Assets : ", icon="ADD")
        for asset_name in manually_added:
            # Determine asset type and icon
            parts = asset_name.split('_')
            asset_type = "FX" if len(parts) > 2 and parts[2].startswith("FX") else (parts[1] if len(parts) > 1 else None)
            if asset_name == "MM_Camera":
                icon = 'VIEW_CAMERA'
            elif asset_type == 'CHR':
                icon = 'OUTLINER_OB_ARMATURE'
            elif asset_type == 'PRP':
                icon = 'ASSET_MANAGER'
            elif asset_type == 'SET':
                icon = 'HOME'
            elif label == 'ITM':
                icon = 'MESH_CUBE'
            elif label == 'FX':
                icon = 'SHADERFX'
            else:
                icon = 'PACKAGE'
            
            asset_row = box.row(align=True)
            asset_row.use_property_split = False
            asset_row.alignment = 'LEFT'
            prop_name = f"buildshot_{asset_name}"
            if hasattr(kitsu_scene, prop_name):
                asset_row.prop(kitsu_scene, prop_name, text="")
            asset_row.label(text=asset_name, icon=icon)
            
            # Check if asset file exists
            asset_path = get_asset_path(asset_name, asset_dir)
            if asset_path and not os.path.exists(asset_path):
                asset_row.label(text="File missing", icon="ERROR")

def draw_linking_options(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw linking options section with button to link assets and audio"""
    layout.label(text="Linking Operator Options :")
    row = layout.row(align=True)
    split = row.split(factor=0.5, align=True)

    col = split.column(align=True)
    col.operator(
        "kitsu.link_selected_assets",
        text="Link selected Assets",
        icon='LINK_BLEND'
    )

    col = split.column(align=True)
    col.operator(
        "kitsu.link_audio",
        text="Link Audio",
        icon='SOUND'
    )
#Insert below image ref linking operator and remove image ref linking operator
    row = layout.row(align=True)
    split = row.split(factor=0.5, align=True)
    col = split.column(align=True)
    col.operator(
        "kitsu.link_image_ref",
        text="Link Image Ref",
        icon='IMAGE_DATA'
    )
    col = split.column(align=True)
    col.operator(
        "kitsu.remove_link_image_ref",
        text="Remove Image Ref",
        icon='CANCEL'
    )


    layout.separator()


"""
Core utilities for build_shot addon
"""


def get_shot_dir(prod_dir, episode, sequence, shot, department, task_type=None):
    # Default empty string to None for non-Animation folders
    if not task_type or department != 'Animation':
        task_type = ""
    
    return os.path.join(prod_dir, "screening", episode, "Scenes", sequence, shot, department, task_type)


def set_shot_filepath(prod_dir, episode, sequence, shot, department, task_type=None):
    seq = int(sequence or "001")
    sequence_str = f"{seq:03d}"
    shot_dir = get_shot_dir(prod_dir, episode, sequence_str, shot, department, task_type)
    if department == 'Animation' :
        task = "An"
    elif department == 'Layout' :
        task = "La"
    else :
        task = department[:3]
    if task:
        filename = f"MM_{episode}_{sequence_str}_{shot}_{task}_v01_x12.blend"
    else :
        raise ValueError(f"Unknown type folder: {department}")
    return os.path.join(shot_dir, filename)


def get_asset_path(asset_name, asset_dir):

    # parts = asset_name.split('_')
    # asset_type = "FX" if len(parts) > 2 and parts[2].startswith("FX") else (parts[1] if len(parts) > 1 else None)
    asset_type = asset_name.split('_')[1] if len(asset_name.split('_')) > 1 else None

    if asset_type == 'CHR':
        return os.path.join(
            asset_dir, "Characters", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'PRP':
        return os.path.join(
            asset_dir, "Props", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'ITM':
        return os.path.join(
            asset_dir, "SetItems", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'SET':
        return os.path.join(
            asset_dir, "Sets", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    # elif asset_type == 'FX':
    #     return os.path.join(
    #         asset_dir, "SetItems", asset_name, 
    #         "Final", "Render", f"{asset_name}.blend"
    #     )
    elif asset_name == "MM_Camera":
        return os.path.join(
            asset_dir, "Camera", f"{asset_name}.blend"
        )
    else:
        return None


def set_frames_timeline(context):
    scene = context.scene
    shot = cache.shot_active_get()
    if not shot:
        return
    if shot.frame_in is not None:
        scene.frame_start = shot.frame_in
    elif shot.frame_out is not None:
        scene.frame_end = shot.frame_out
    else :
        scene.frame_start = 1
        scene.frame_end = shot.nb_frames


def get_audio_path(prod_dir, episode, shot):
    """
    Get the full path to an audio file for a given episode and shot.
    
    Args:
        episode: Episode number (e.g., "118")
        shot: Shot number (e.g., "0220")
        prod_dir: Production directory root (default: R:\melodyandmomon)
    
    Returns:
        Full path to the audio .wav file
    """
    audio_folder = os.path.join(
        prod_dir,
        "screening",
        episode,
        f"EP{episode}_Material",
        "AUDIO_VIDEO",
        "Single_Shot_Audio_01",
    )
    audio_folder = audio_folder
    sound_name = f"MM_{episode}_{shot}.wav"
    return os.path.join(audio_folder, sound_name)

def import_sound_strip(context):
    scene = context.scene
    # Safely construct episode/shot strings
    prod_dir = str(prefs.project_root_dir_get(context))
    ep = cache.episode_active_get().name
    shot = cache.shot_active_get().name

    sound_name = f"MM_{ep}_{shot}.wav"
    sound_path = get_audio_path(prod_dir, ep, shot)

    # Validate file existence before attempting to load
    if not os.path.isfile(sound_path):
        msg = f"Audio file not found: {sound_path}"
        return None

    # try:
    #     sound_data = bpy.data.sounds.load(sound_path, check_existing=True)
    # except Exception as e:
    #     print(f"Failed to load sound '{sound_path}': {e}")
    #     raise
    # === PREPARE SEQUENCE EDITOR ===
    # Ensure we have a sequence editor in the current scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    # === ADD SOUND STRIP ===
    if not sound_name in scene.sequence_editor.sequences :
        try:
            # Add the sound strip starting at frame 1 on channel 1
            sound_strip = scene.sequence_editor.sequences.new_sound(
                name=sound_name,
                filepath=sound_path,
                channel=1,
                frame_start=1
            )

            # Optional: Adjust volume
            sound_strip.volume = 1.0  # 1.0 = 100%

            print(f"Sound strip added: {sound_strip.name} at frame {sound_strip.frame_start}")
        except Exception as e:
            print(f"Failed to add sound strip: {e}")

    sound_strip = scene.sequence_editor.sequences[sound_name]
    sound_strip.channel = 1
    sound_strip.frame_start = 1

    # bpy.context.scene.sequence_editor.sequences[sound_name]
    bpy.context.scene.frame_end = sound_strip.frame_final_duration

def import_image_ref(context):
    scene = context.scene
    # Safely construct episode/shot strings
    prod_dir = str(prefs.project_root_dir_get(context))
    episode = cache.episode_active_get()
    shot = cache.shot_active_get()

    image_name = f"MM_{episode.name}_{shot.name}.mov"

    image_path = os.path.join(prod_dir, "screening" , episode.name, f"EP{episode.name}_Material","AUDIO_VIDEO", "Single_Shot_01", image_name)

    # image_data = bpy.data.images.load(image_path, check_existing=True)

    img = bpy.data.images.load(image_path, check_existing=True)
    camera = scene.camera
    camera.data.show_background_images = True
    bg = camera.data.background_images.new()
    bg.image = img
    bg.image_user.frame_start = 1
    bg.image_user.frame_duration = img.frame_duration

def create_collection_for_asset(candidate_path):
    """
    Link la collection qui a le même nom que le fichier .blend
    """

    if not os.path.exists(candidate_path):
        print(f"[ERROR] .blend introuvable : {candidate_path}")
        return None

    expected_name = os.path.splitext(os.path.basename(candidate_path))[0]
    is_env = False
    if expected_name.split('_')[1] == 'CHR':
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'chara'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("Chara")
        expected_col.color_tag = 'COLOR_01'
    elif expected_name.split('_')[1] == 'PRP':
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'props'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("Props")
        expected_col.color_tag = 'COLOR_05'
    elif expected_name.split('_')[1] == 'SET':
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'env'.casefold()), None)
        expected_name = os.path.splitext(os.path.basename(candidate_path))[0].split("_")[2]
        is_env = True
        if expected_col is None :
            expected_col = bpy.data.collections.new("Env")
    elif len(expected_name.split('_')) >2 and expected_name.split('_')[2].startswith("FX"):
    # elif expected_name.split('_')[2].startswith("FX") :
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'fx'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("FX")
        expected_col.color_tag = 'COLOR_06'
    # elif expected_name.split('_')[1] == "ITM" :
    elif expected_name.split('_')[1] == "ITM" and not expected_name.split('_')[2].startswith("FX") :
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'setitems'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("SetItems")
        expected_col.color_tag = 'COLOR_02'
    elif expected_name.split('_')[1] == "Camera" :
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'cam'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("Cam")
        expected_col.color_tag = 'COLOR_04'
    #Link collection to scene if not already
    if not expected_col in list(bpy.context.scene.collection.children) :
        bpy.context.scene.collection.children.link(expected_col)
    return expected_col

def link_and_override_collection(candidate_path):

    if not os.path.exists(candidate_path):
        print(f"[ERROR] .blend introuvable : {candidate_path}")
        return None

    expected_name = os.path.splitext(os.path.basename(candidate_path))[0]
    expected_col = create_collection_for_asset(candidate_path)
    is_env = False
    if expected_name.split('_')[1] == 'SET':
        is_env = True
    try:
        with bpy.data.libraries.load(candidate_path, link=True, relative=False) as (data_from, data_to):
            if not is_env:
                if expected_name not in data_from.collections:
                    return None
                
                data_to.collections = [expected_name]

            else:
                data_to.collections = list(data_from.collections)

        if is_env:
            loaded_cols = data_to.collections
            child_names = set()

            for col in loaded_cols:
                for child in col.children:
                    child_names.add(child.name)

            root_cols = [col for col in loaded_cols if col.name not in child_names]

            if not root_cols:
                print("[ERROR] Aucune collection racine trouvée")
                return None

            linked_col = root_cols[0]

        else:
            linked_col = data_to.collections[0]
            

        if not is_env :
            override_col = linked_col.override_hierarchy_create(
                scene=bpy.context.scene,
                view_layer=bpy.context.view_layer,
                do_fully_editable=True
        
        )
        
        else :
            override_col = linked_col
        if expected_col is not None:
            if override_col.name not in expected_col.children:
                expected_col.children.link(override_col)
        for col in bpy.context.scene.collection.children :
            if override_col == col :
                bpy.context.scene.collection.children.unlink(override_col)      
        print(f"[OK] {expected_name} linkée depuis {candidate_path}")
        return override_col

    except Exception as e:
        print(f"[ERROR] Échec du link '{expected_name}'")
        print(f"        {e}")
        return None


def link_selected_assets(context):
    """Link selected assets for the active shot, including manually-added assets."""
    scene = context.scene
    kitsu_scene = scene.kitsu
    shot_active = cache.shot_active_get() 
    shot_assets = shot_active.get_all_assets()
    asset_dir = prefs.asset_dir_get(context)
    
    if not shot_assets:
        raise ValueError("No assets found for this shot")
    if not os.path.exists(asset_dir):
        raise FileNotFoundError("Could not find production directory")
    
    # Build set of shot asset names for efficient lookup
    shot_asset_names = {a.name for a in shot_assets}
    
    # Find and add manually-added assets from project assets
    buildshot_props = {
        attr_name.replace("buildshot_", ""): attr_name
        for attr_name in dir(kitsu_scene)
        if attr_name.startswith("buildshot_")
    }
    
    manually_added = {name for name in buildshot_props.keys() if name not in shot_asset_names}
    
    if manually_added:
        project_assets = cache.get_all_assets_enum(context, asset_scope='PROJECT')
        # project_assets is now a list of (id, name, description) tuples
        project_asset_names = {asset_tuple[1] for asset_tuple in project_assets}
        
        # Find manually-added assets that exist in project assets
        valid_manually_added = manually_added & project_asset_names
        for asset_name in valid_manually_added:
            print(f"Found manually-added asset '{asset_name}' in project assets")
    
    
    # print("Assets to link: ", [a.name for a in shot_assets])
    # Check if any asset has a buildshot property
    has_buildshot_props = any(hasattr(kitsu_scene, f"buildshot_{a.name}") for a in shot_assets)
    
    success_count = 0
    failed_assets = []
    
    for asset in shot_assets:
        asset_name = asset.name
        # Skip if asset has buildshot property set to False
        if has_buildshot_props:
            prop_name = f"buildshot_{asset_name}"
            if hasattr(kitsu_scene, prop_name) and not getattr(kitsu_scene, prop_name):
                continue
        
        # Get and validate asset path
        asset_path = get_asset_path(asset_name, asset_dir)
        if asset_path is None:
            failed_assets.append(f"{asset_name} (unknown type)")
            continue
        
        if not os.path.exists(asset_path):
            failed_assets.append(f"{asset_name} (file not found)")
            continue
        
        # Link the asset
        print(f"Linking asset '{asset_name}' from path: {asset_path}")
        result = link_and_override_collection(asset_path)
        if result:
            success_count += 1
        else:
            failed_assets.append(asset_name)
    
    return {
        'success_count': success_count,
        'failed_assets': failed_assets
    }


#func find previous shot path
def find_previous_shot(context=None):
    """Find the previous shot in the sequence. Returns shot name or None."""
    if context is None:
        context = bpy.context
    
    shots = cache.get_shots_enum_for_active_seq(context, context)
    active_shot = cache.shot_active_get()
    if not active_shot:
        return None
    active_shot_name = active_shot.name
    if active_shot_name in shots:
        idx = shots.index(active_shot_name)
        if idx > 0:
            return shots[idx-1]
    return None


def get_highest_version_file(filepath):
    """Find the highest version of a file based on version number in filename."""
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    _, ext = os.path.splitext(filepath)
    
    if not os.path.exists(directory):
        return None
    
    matching_files = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            file_name_without_ext = os.path.splitext(file)[0]
            try:
                version = int(file_name_without_ext[-2:][1:])
                matching_files.append((version, os.path.join(directory, file)))
            except (ValueError, IndexError):
                continue
    
    if matching_files:
        matching_files.sort(reverse=True)
        return matching_files[0][1]
    
    return filepath if os.path.exists(filepath) else None


def set_scene_settings(context):
    """Set render settings for shot output as shown in render panel"""
    scene = bpy.context.scene
    render = scene.render
    
    # === Resolution ===
    render.resolution_x = 1280
    render.resolution_y = 720
    render.pixel_aspect_x = 1.0
    render.pixel_aspect_y = 1.0
    
    # === Frame Rate ===
    scene.render.fps = 25
    
    # === Output Format ===
    render.image_settings.file_format = 'FFMPEG'
    render.image_settings.color_mode = 'RGB'
    
    # === FFmpeg Settings ===
    render.ffmpeg.format = 'QUICKTIME'
    render.ffmpeg.codec = 'H264'
    render.ffmpeg.constant_rate_factor = 'MEDIUM'
    render.ffmpeg.ffmpeg_preset = 'GOOD'
    render.ffmpeg.gopsize = 18
    render.ffmpeg.use_max_b_frames = False
    render.ffmpeg.max_b_frames = 0
    
    # === Metadata ===
    render.metadata_input = 'SCENE'
    render.use_file_extension = False
    render.use_stamp = True
    render.use_stamp_date = False
    render.use_stamp_time = False
    render.use_stamp_render_time = False
    render.use_stamp_frame = True
    render.use_stamp_frame_range = False
    render.use_stamp_memory = False
    render.use_stamp_hostname = False
    render.use_stamp_camera = False
    render.use_stamp_scene = False
    render.use_stamp_marker = False
    render.use_stamp_filename = True
    render.use_stamp_lens = True
    render.stamp_font_size = 10
    render.stamp_background = (0, 0, 0, 1)

    
    #If asset camera exists set bpy.data.scenes["Scene"].camera to it
    if "MM_Camera" in bpy.data.objects:
        bpy.data.scenes["Scene"].camera = bpy.data.objects["MM_Camera"]

    print("[OK] Scene render settings configured")

def set_render_filepath(context):
    """Set render output path for the current shot"""
    scene = bpy.context.scene
    episode = cache.episode_active_get()
    shot = cache.shot_active_get()
    task_name = scene.copy_output.copy_output_layer
    output_path = get_new_output_path(bpy.context)
    file_name = "_".join(filter(None, ["MM", episode.name, shot.name, task_name,])) + ".mov"
    playblast_path = Path(output_path).parent.joinpath("playblast", file_name).as_posix()
    # print(f"[OK] Render filepath set to: {playblast_path}")
    if output_path:
        return playblast_path
    else:
        print("[ERROR] Failed to compute render filepath")

# def load actions from previous shot for each CHR and PRP if build_shot true
def append_previous_frame_from_previous_shot(scene):
    """Load actions from the last frame of the previous shot for each asset marked as buildshot=True"""
    shot_active = cache.shot_active_get()
    kitsu_scene = scene.kitsu
    
    if not shot_active:
        raise ValueError("No active shot selected")
    
    # Get assets for the selected shot
    assets = shot_active.get_all_assets()
    
    if not assets:
        raise ValueError("No assets found for this shot")
    
    # Find the previous shot
    previous_shot_name = find_previous_shot()
    if not previous_shot_name:
        print("[INFO] No previous shot found")
        return
    
    # Build path to previous shot file
    prod_dir = prefs.prod_dir_get(bpy.context)
    episode = cache.episode_active_get()
    sequence = cache.sequence_active_get()
    department = cache.department_active_get()
    task_type = cache.task_type_department_active_get()
    
    previous_shot_path = set_shot_filepath(
        prod_dir=prod_dir,
        episode=episode.name,
        sequence=sequence.name,
        shot=previous_shot_name,
        department=department.name,
        task_type=task_type.name
    )
    
    # Get the highest version of the previous shot file
    previous_shot_file = get_highest_version_file(previous_shot_path)
    
    if not previous_shot_file or not os.path.exists(previous_shot_file):
        print(f"[WARNING] Previous shot file not found: {previous_shot_path}")
        return
    
    print(f"[INFO] Loading actions from previous shot: {previous_shot_file}")
    
    # If dynamic BoolProperties exist for assets, only append those checked.
    has_props = any(hasattr(kitsu_scene, f"buildshot_{a.name}") for a in assets)
    
    for asset in assets:
        asset_name = asset.name
        
        # Skip if buildshot property exists and is False
        if has_props:
            prop_name = f"buildshot_{asset_name}"
            if hasattr(kitsu_scene, prop_name) and not getattr(kitsu_scene, prop_name):
                continue
        
        # Only process CHR and PRP assets (those with animations)
        asset_type = asset_name.split('_')[1] if len(asset_name.split('_')) > 1 else None
        if asset_type not in ('CHR', 'PRP'):
            continue
        
        try:
            # Append actions from previous shot file
            with bpy.data.libraries.load(previous_shot_file, link=False, relative=False) as (data_from, data_to):
                # Find actions belonging to this asset
                matching_actions = [a for a in data_from.actions if asset_name.lower() in a.lower()]
                if matching_actions:
                    data_to.actions = matching_actions
                    print(f"[OK] Loaded {len(matching_actions)} action(s) for {asset_name} from previous shot")
                else:
                    print(f"[INFO] No actions found for {asset_name} in previous shot")
        except Exception as e:
            print(f"[ERROR] Failed to load actions for {asset_name}: {e}")


def get_new_output_path(context: bpy.types.Context) -> str | None:
    """Compute and return the output path for the current shot"""
    return set_shot_filepath(
        prefs.project_root_dir_get(context),
        cache.episode_active_get().name,
        cache.sequence_active_get().name,
        cache.shot_active_get().name,
        cache.department_active_get().name,
        cache.task_type_department_active_get().name
    )

def get_next_task_type(shot, task_type_name):
    # 1. Get ALL task types of shot
    task_types = shot.get_all_task_types()

    # tri par priorité
    task_types_sorted = sorted(task_types, key=lambda t: t.priority)

    # 2. Find current task type
    current_task_type = next(
        (t for t in task_types_sorted if t.name == task_type_name),
        None
    )

    # fallback : cas /Layout/file.blend
    if not current_task_type:
        current_task_type = next(
            (t for t in task_types_sorted if t.name == task_type_name),
            None
        )

    # 3. Get NEXT task type
    task_type = None
    if current_task_type:
        for t in task_types_sorted:
            if t.priority > current_task_type.priority:
                task_type = t
                break
    return task_type

def get_sorted_task_types_for_shot(shot):
    task_types = shot.get_all_task_types()
    return sorted(task_types, key=lambda t: t.priority)

def init_modeling_scene_setup():
    """Set up the scene for modeling tasks (e.g., set viewport to solid, set shading to material preview)"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
                    space.viewport_shade = 'MATERIAL'
    #Find asset in cache with asset type == Camera and link it to the scene, not MM_Camera just the only asset with asset type = Camera
    #Camera placement : set location to (0,-3,0.5) 
    # bpy.context.scene.cursor.location = (0, -3, 0.5)
    camera_assets = [a for a in cache.get_all_assets_enum(bpy.context) if 'Camera' in a.name]
    if camera_assets:
        camera_asset = camera_assets[0]
        asset_path = get_asset_path(camera_asset.name, prefs.asset_dir_get(bpy.context))
        if asset_path and os.path.exists(asset_path):
            link_and_override_collection(asset_path)

def init_rigging_scene_setup(asset):
    asset_name = asset.name
    task_type_active = cache.task_type_active_get()
    #Copy modeling file to rigging folder, open copy
    asset_dir = prefs.asset_dir_get(bpy.context)
    modeling_path = os.path.join(asset_dir, asset_name, "Modeling", asset_name+"_Modeling"+".blend")
    if modeling_path and os.path.exists(modeling_path):
        rigging_path = os.path.join(asset_dir, asset_name, task_type_active.name, asset_name+"_"+task_type_active.short_name+".blend")
    #append collection with asset name
    with bpy.data.libraries.load(rigging_path, link=False) as (data_from, data_to):
        if asset_name in data_from.collections:
            data_to.collections = [asset_name]
        else:
            print(f"[ERROR] Collection '{asset_name}' not found in {rigging_path}")
            return
    #Create WGTS collection children asset.name col
    asset_col = data_to.collections[0]

    wgts_col = bpy.data.collections.new("WGTS")
    asset_col.children.link(wgts_col)
    wgts_col.hide_viewport = False
    
    rig_col = bpy.data.collections.new(f"{asset_name}_rig")
    asset_col.children.link(rig_col)

    #Add armature object to rig collection
    armature_data = bpy.data.armatures.new(f"{asset_name}_rig")
    armature_obj = bpy.data.objects.new(f"{asset_name}_rig", armature_data)
    rig_col.objects.link(armature_obj)
    #Bone creation
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    pose_bone_data = armature_data.edit_bones.new("pose")
    traj_bone_data = armature_data.edit_bones.new("traj")
    pose_bone_data.head = (0, 0, 0)
    pose_bone_data.tail = (0, 1, 0)
    traj_bone_data.head = (0, 0, 0)
    traj_bone_data.tail = (0, 1, 0)
    traj_bone_data.parent = pose_bone_data
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    pose_bone = armature_obj.pose.bones["pose"]
    traj_bone = armature_obj.pose.bones["traj"]

    #Custom shape cration function 
    def create_circle_with_arrows(name, col, radius=0.1, arrow_length=0.2):
        vertices = [(1.5807852745056152, 0.0, 0.0), (1.280785322189331, -0.39509034156799316, 0.0), (1.280785322189331, -0.19509035348892212, 0.0), (0.9807852506637573, -0.19509035348892212, 0.0), (0.9238795042037964, -0.3826834261417389, 0.0), (0.8314696550369263, -0.5555701851844788, 0.0), (0.7071067690849304, -0.7071067690849304, 0.0), (0.5555717945098877, -0.8314685821533203, 0.0), (0.3826850652694702, -0.9238788485527039, 0.0), (0.19509197771549225, -0.9807849526405334, 0.0), (0.19509197771549225, -1.2807848453521729, 0.0), (0.3950919806957245, -1.2807848453521729, 0.0), (0.0, -1.5807849168777466, 0.0), (-0.3950919806957245, -1.2807848453521729, 0.0), (-0.19509197771549225, -1.2807848453521729, 0.0), (-0.19509197771549225, -0.9807849526405334, 0.0), (-0.3826850652694702, -0.9238788485527039, 0.0), (-0.5555717945098877, -0.8314685821533203, 0.0), (-0.7071067690849304, -0.7071067690849304, 0.0), (-0.8314696550369263, -0.5555701851844788, 0.0), (-0.9238795042037964, -0.3826834261417389, 0.0), (-0.9807852506637573, -0.19509035348892212, 0.0), (-1.280785322189331, -0.19509035348892212, 0.0), (-1.280785322189331, -0.39509034156799316, 0.0), (-1.5807852745056152, 0.0, 0.0), (-1.280785322189331, 0.39509034156799316, 0.0), (-1.280785322189331, 0.19509035348892212, 0.0), (-0.9807852506637573, 0.19509035348892212, 0.0), (-0.9238795042037964, 0.3826834261417389, 0.0), (-0.8314696550369263, 0.5555701851844788, 0.0), (-0.7071067690849304, 0.7071067690849304, 0.0), (-0.5555717945098877, 0.8314685821533203, 0.0), (-0.3826850652694702, 0.9238788485527039, 0.0), (-0.19509197771549225, 0.9807849526405334, 0.0), (-0.19509197771549225, 1.2807848453521729, 0.0), (-0.3950919806957245, 1.2807848453521729, 0.0), (0.0, 1.5807849168777466, 0.0), (0.3950919806957245, 1.2807848453521729, 0.0), (0.19509197771549225, 1.2807848453521729, 0.0), (0.19509197771549225, 0.9807849526405334, 0.0), (0.3826850652694702, 0.9238788485527039, 0.0), (0.5555717945098877, 0.8314685821533203, 0.0), (0.7071067690849304, 0.7071067690849304, 0.0), (0.8314696550369263, 0.5555701851844788, 0.0), (0.9238795042037964, 0.3826834261417389, 0.0), (0.9807852506637573, 0.19509035348892212, 0.0), (1.280785322189331, 0.19509035348892212, 0.0), (1.280785322189331, 0.39509034156799316, 0.0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32), (32, 33), (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 0)]


        mesh = bpy.data.meshes.new(f"WGT_{name}")
        obj = bpy.data.objects.new(f"WGT_{name}", mesh)

        col.objects.link(obj)

        mesh.from_pydata(vertices, edges, [])
        mesh.update()

        return obj

    def create_square(name, col, size=0.6):
        vertices = [(-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]

        mesh = bpy.data.meshes.new(f"WGT_{name}")
        obj = bpy.data.objects.new(f"WGT_{name}", mesh)
        
        col.objects.link(obj)

        mesh.from_pydata(vertices, edges, [])
        mesh.update()

        return obj

    #Add custom shape to traj, circle with arrow on each side 
    pose_custom_shape = create_circle_with_arrows(pose_bone_data.name, wgts_col)
    traj_custom_shape = create_square(traj_bone_data.name, wgts_col)

    pose_bone.custom_shape = pose_custom_shape
    traj_bone.custom_shape = traj_custom_shape


# def update_model(context):
    