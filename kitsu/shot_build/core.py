import bpy
import os
from .. import cache, bkglobals, prefs

# Category values are defined in enum props.py KITSU_property_group_scene under category
def is_edit_context():
    return bpy.context.scene.kitsu.category == "EDIT"


def is_sequence_context():
    return bpy.context.scene.kitsu.category == "SEQ"


def is_asset_context():
    return bpy.context.scene.kitsu.category == "ASSET"


def is_shot_context():
    return bpy.context.scene.kitsu.category == "SHOT"


"""
Core utilities for build_shot addon
"""

def get_filtered_assets(context, asset_filter='ALL', asset_scope='PROJECT'):
    """
    Get assets optionally filtered by type and scope.
    Wrapper around cache function for backward compatibility.
    
    Args:
        context: Blender context
        asset_filter: Filter type - 'ALL', 'CHR', 'PRP', 'SET', 'ITM'
        asset_scope: Asset scope - 'PROJECT' for all assets, 'SHOT' for shot-specific
        
    Returns:
        List of filtered assets
    """
    return cache.get_filtered_assets_for_buildshot(context, asset_filter, asset_scope)


def get_audio_folder(prod_dir, episode):
    """
    Get the path to the audio folder for a given episode.
    
    Args:
        episode: Episode number (e.g., "118")
        prod_dir: Production directory root (default: R:\melodyandmomon)
    
    Returns:
        Full path to the audio folder
    """
    return os.path.join(
        prod_dir,
        "screening",
        episode,
        f"EP{episode}_Material",
        "AUDIO_VIDEO",
        "Single_Shot_Audio_01",
    )


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
    audio_folder = get_audio_folder(prod_dir, episode)
    sound_name = f"MM_{episode}_{shot}.wav"
    return os.path.join(audio_folder, sound_name)


def get_shot_dir(prod_dir, episode, sequence, shot, type_folder, anim_sub_folder=None):
    # Default empty string to None for non-Animation folders
        
    if not anim_sub_folder or type_folder != 'Animation':
        anim_sub_folder = ""
    
    return os.path.join(prod_dir, "screening", episode, "Scenes", sequence, shot, type_folder, anim_sub_folder)


def set_shot_filepath(prod_dir, episode, sequence, shot, type_folder, anim_sub_folder=None):
    seq = int(sequence or "001")
    sequence_str = f"{seq:03d}"
    shot_dir = get_shot_dir(prod_dir, episode, sequence_str, shot, type_folder, anim_sub_folder)
    if type_folder == 'Animation' :
        task = "An"
    elif type_folder == 'Layout' :
        task = "La"
    filename = f"MM_{episode}_{sequence_str}_{shot}_{task}_v01_x12.blend"
    return os.path.join(shot_dir, filename)


def get_asset_path(asset_name, asset_dir):

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


def link_collection_matching_filename(candidate_path):
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
            bpy.context.scene.collection.children.link(expected_col)
            expected_col.color_tag = 'COLOR_01'
    elif expected_name.split('_')[1] == 'PRP':
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'props'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("Props")
            bpy.context.scene.collection.children.link(expected_col)
            expected_col.color_tag = 'COLOR_05'
    elif expected_name.split('_')[1] == 'SET':
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'env'.casefold()), None)
        expected_name = os.path.splitext(os.path.basename(candidate_path))[0].split("_")[2]
        is_env = True
        if expected_col is None :
            expected_col = bpy.data.collections.new("Env")
            bpy.context.scene.collection.children.link(expected_col)
    elif expected_name.split('_')[1] == "ITM" :
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'setitems'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("SetItems")
            bpy.context.scene.collection.children.link(expected_col)
            expected_col.color_tag = 'COLOR_02'
    elif expected_name.split('_')[1] == "Camera" :
        expected_col = next((c for c in bpy.data.collections if c.name.casefold() == 'cam'.casefold()), None)
        if expected_col is None :
            expected_col = bpy.data.collections.new("Cam")
            expected_col.color_tag = 'COLOR_04'
            bpy.context.scene.collection.children.link(expected_col)

    try:
        with bpy.data.libraries.load(candidate_path, link=True, relative=False) as (data_from, data_to):

            if not is_env:
                print("Link d'un asset")

                if expected_name not in data_from.collections:
                    # print(f"[WARNING] '{expected_name}' absente de {candidate_path}")
                    return None

                # cas simple : on link direct par nom
                data_to.collections = [expected_name]

            else:
                print("Link d'un env")

                # 1) on charge TOUTES les collections
                data_to.collections = list(data_from.collections)

        # 2) post-traitement APRÈS le with
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
        if override_col in bpy.context.scene.collection.children_recursive:
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
        for attr_name in dir(scene)
        if attr_name.startswith("buildshot_")
    }
    
    manually_added = {name for name in buildshot_props.keys() if name not in shot_asset_names}
    
    if manually_added:
        project_assets = cache.get_filtered_assets_for_buildshot(
            context, asset_filter='ALL', asset_scope='PROJECT'
        )
        project_assets_by_name = {a.name: a for a in project_assets}
        
        for asset_name in manually_added:
            if asset_name in project_assets_by_name:
                shot_assets.append(project_assets_by_name[asset_name])
                print(f"Added {asset_name} to shot assets from project assets")
    
    print("Assets to link: ", [a.name for a in shot_assets])
    
    # Check if any asset has a buildshot property
    has_buildshot_props = any(hasattr(scene, f"buildshot_{a.name}") for a in shot_assets)
    
    success_count = 0
    failed_assets = []
    
    for asset in shot_assets:
        asset_name = asset.name
        
        # Skip if asset has buildshot property set to False
        if has_buildshot_props:
            prop_name = f"buildshot_{asset_name}"
            if hasattr(scene, prop_name) and not getattr(scene, prop_name):
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
        result = link_collection_matching_filename(asset_path)
        if result:
            success_count += 1
        else:
            failed_assets.append(asset_name)
    
    return {
        'success_count': success_count,
        'failed_assets': failed_assets
    }


def draw_assets_for_shot(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw assets available for the selected shot plus any manually-added assets"""
    scene = context.scene
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
    for attr_name in dir(scene):
        if attr_name.startswith("buildshot_"):
            asset_name = attr_name.replace("buildshot_", "")
            if asset_name not in shot_asset_names and hasattr(scene, attr_name):
                manually_added.append(asset_name)
    
    if not shot_assets and not manually_added:
        layout.label(text="No assets found for this shot", icon='INFO')
        return
    
    # Display assets in a box
    box = layout.box()
    
    # Display shot assets organized by type
    if shot_assets:
        box.label(text="Shot Assets : ", icon="PACKAGE")
        for label in ("CHR", "PRP", "SET", "ITM", "CAMERA"):
            items = [a for a in shot_assets if f"_{label}_" in a.name or (label == "CAMERA" and a.name == "MM_Camera")]
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
                    else:
                        icon = 'PACKAGE'
                    asset_row = box.row(align=True)
                    asset_row.use_property_split = False
                    asset_row.alignment = 'LEFT'
                    prop_name = f"buildshot_{asset.name}"
                    if hasattr(scene, prop_name):
                        asset_row.prop(scene, prop_name, text="")
                    asset_row.label(text=asset.name, icon=icon)
                    
                    # Check if asset file exists
                    asset_path = get_asset_path(asset.name, asset_dir)
                    if asset_path and not os.path.exists(asset_path):
                        asset_row.label(text="File missing", icon="ERROR")
    
    # Display manually-added assets section
    if manually_added:
        box.separator()
        box.label(text="Added Assets : ", icon="ADD")
        for asset_name in manually_added:
            # Determine asset type and icon
            asset_type = asset_name.split('_')[1] if len(asset_name.split('_')) > 1 else None
            if asset_name == "MM_Camera":
                icon = 'VIEW_CAMERA'
            elif asset_type == 'CHR':
                icon = 'OUTLINER_OB_ARMATURE'
            elif asset_type == 'PRP':
                icon = 'ASSET_MANAGER'
            elif asset_type == 'SET':
                icon = 'HOME'
            elif asset_type == 'ITM':
                icon = 'MESH_CUBE'
            else:
                icon = 'PACKAGE'
            
            asset_row = box.row(align=True)
            asset_row.use_property_split = False
            asset_row.alignment = 'LEFT'
            prop_name = f"buildshot_{asset_name}"
            if hasattr(scene, prop_name):
                asset_row.prop(scene, prop_name, text="")
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
        "build_shot.link_selected_assets",
        text="Link selected Assets",
        icon='LINK_BLEND'
    )

    col = split.column(align=True)
    col.operator(
        "build_shot.link_audio",
        text="Link Audio",
        icon='SOUND'
    )
    layout.separator()


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

def get_shot_name(context):
    scene = context.scene
    episode = cache.episode_active_get()
    if not episode:
        return None
    
    sequence =  cache.sequence_active_get()
    if not sequence:
        return None
    shot = cache.shot_active_get()
    if not shot:
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
    scene = context.scene
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
    render.use_stamp_date = False
    render.use_stamp_time = True
    render.use_stamp_render_time = True
    render.use_stamp_frame = True
    render.use_stamp_frame_range = True
    render.use_stamp_filename = True
    render.use_stamp_lens = True
    
    #If asset camera exists set bpy.data.scenes["Scene"].camera to it
    if "MM_Camera" in bpy.data.objects:
        bpy.data.scenes["Scene"].camera = bpy.data.objects["MM_Camera"]
    
    print("[OK] Scene render settings configured")



# def load actions from previous shot for each CHR and PRP if build_shot true
def append_previous_frame_from_previous_shot(scene):
    """Load actions from the last frame of the previous shot for each asset marked as buildshot=True"""
    shot_active = cache.shot_active_get()
    
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
    
    previous_shot_path = set_shot_filepath(
        prod_dir=prod_dir,
        episode=episode.name,
        sequence=sequence.name,
        shot=previous_shot_name,
        type_folder=scene.build_shot.selected_task_type,
        anim_sub_folder=scene.build_shot.anim_sub_folder
    )
    
    # Get the highest version of the previous shot file
    previous_shot_file = get_highest_version_file(previous_shot_path)
    
    if not previous_shot_file or not os.path.exists(previous_shot_file):
        print(f"[WARNING] Previous shot file not found: {previous_shot_path}")
        return
    
    print(f"[INFO] Loading actions from previous shot: {previous_shot_file}")
    
    # If dynamic BoolProperties exist for assets, only append those checked.
    has_props = any(hasattr(scene, f"buildshot_{a}") for a in assets)
    
    for asset in assets:
        asset_name = asset.name
        
        # Skip if buildshot property exists and is False
        if has_props:
            prop_name = f"buildshot_{asset_name}"
            if hasattr(scene, prop_name) and not getattr(scene, prop_name):
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