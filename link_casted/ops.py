# link_casted/ops.py
import bpy
import os
from .properties import update_scene_properties
from .core import find_file, match_shot, link_collection_matching_filename, find_dir_ep
from .cache import update_cache

class LINKCASTED_OT_load_files(bpy.types.Operator):
    bl_idname = "linkcasted.load_files"
    bl_label = "Load Files"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        update_scene_properties(scene)
        # Precompute and cache the categorized link properties so the UI
        # draw() doesn't need to scan and categorize every time.
        update_cache(scene)
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
    

class LINKCASTED_OT_unlink_collection(bpy.types.Operator):
    bl_idname = "linkcasted.unlink_asset_to_collection"
    bl_label = "Unlink uncasted Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        scene_props = {prop for prop in dir(scene) if prop.startswith("link_")}

        libs_to_remove = []
        cols_to_remove = []
        save_libs = set()

        # Collect library filenames referenced by collections in the scene (recursively)
        # Loop through top-level collections in the current scene
        for col in bpy.context.scene.collection.children:
            # Loop through sub-collections
            for subcol in col.children:
                if f"link_{os.path.splitext(subcol.name)[0]}" in scene_props : continue
                if hasattr(subcol.library, "filepath") :
                    lib_basename = os.path.splitext(os.path.basename(subcol.library.filepath))[0]
                    if f"link_{os.path.splitext(lib_basename)[0]}" in scene_props : continue
                    cols_to_remove.append(subcol)
                    libs_to_remove.append(lib_basename)
                # Check if the sub-collection is linked from a library
                if hasattr(subcol, "override_library") :
                    libs_to_remove.append(subcol.override_library.reference.library)
                    cols_to_remove.append(subcol)
        # --------------------------------------------------
        # 3. Suppression des collections liées
        # --------------------------------------------------

        removed_collections = 0

        for lib in libs_to_remove:
            # Determine base name for the library (without extension)
            lib_name = os.path.basename(getattr(lib, "filepath", lib.name) or lib.name)
            lib_base = os.path.splitext(lib_name)[0]

            print(f"[LIB] Suppression de {lib.name} (base={lib_base})")

            # Remove collections whose name matches the library base or that are linked from this library

            for c in cols_to_remove:
                try:
                    bpy.data.batch_remove(ids=(c,))
                    removed_collections += 1
                except Exception:
                    try:
                        bpy.data.collections.remove(c)
                        removed_collections += 1
                    except Exception:
                        print(f"Failed to remove collection {c.name}")

            # Finally remove the library itself
            try:
                bpy.data.batch_remove(ids=(lib,))
            except Exception:
                try:
                    bpy.data.libraries.remove(lib)
                except Exception:
                    print(f"Failed to remove library {lib.name}")


        self.report(
            {'INFO'},
            f"{len(libs_to_remove)} libraries et {removed_collections} collections supprimées"
        )

        return {'FINISHED'}


class LINKCASTED_OT_link_sounds(bpy.types.Operator):
    bl_idname = "linkcasted.link_sounds"
    bl_label = "Link Sounds"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        def clean_blend_name(blend_path):
            """
            Extracts the base name from a .blend file path, removes '001' parts,
            and clears parts after index 3.
            """
            if not isinstance(blend_path, str) or not blend_path.strip():
                raise ValueError("blend_path must be a non-empty string.")

            # Get filename without extension
            blend_name = os.path.splitext(os.path.basename(blend_path))[0]

            # Split into parts by underscore
            parts = blend_name.split("_")

            for i, part in enumerate(parts):
                # Remove '001'
                if part == "001":
                    parts[i] = ""
                # Remove anything after index 3
                if i > 3:
                    parts[i] = ""

            # Join parts, removing empty ones and avoiding double underscores
            cleaned_name = "_".join(filter(None, parts))
            return cleaned_name  
        blend_path = bpy.data.filepath
        ep_dir = find_dir_ep(blend_path)  
        sound_name = clean_blend_name(blend_path) + ".wav"     
        sound_path = os.path.join(ep_dir, "EP118_Material", "AUDIO_VIDEO","Single_Shot_Audio_01",sound_name )

        blend_name = clean_blend_name(blend_path)  


        sound_data = bpy.data.sounds.load(sound_path, check_existing=True)

        # Validate file existence
        if not os.path.isfile(sound_path):
            raise FileNotFoundError(f"Audio file not found: {sound_path}")

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

                print(f"✅ Sound strip added: {sound_strip.name} at frame {sound_strip.frame_start}")
            except Exception as e:
                print(f"❌ Failed to add sound strip: {e}")

        sound_strip = scene.sequence_editor.sequences[sound_name]
        sound_strip.channel = 1
        sound_strip.frame_start = 1

        # bpy.context.scene.sequence_editor.sequences[sound_name]
        bpy.context.scene.frame_end = sound_strip.frame_final_duration + 1


        return {'FINISHED'}
#register unregister property
classes = (LINKCASTED_OT_load_files, LINKCASTED_OT_link_collection, LINKCASTED_OT_unlink_collection, LINKCASTED_OT_link_sounds,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        # Remove dynamic scene properties created by update_scene_properties (named like "link_<basename>")
        # for attr in [a for a in dir(bpy.types.Scene) if a.startswith("link_")]:
        #     try:
        #         delattr(bpy.types.Scene, attr)
        #     except Exception:
        #         pass