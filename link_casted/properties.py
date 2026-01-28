import bpy
import os
from .core import find_file, match_shot
from .core import find_dir_ep

def clear_link_properties():
    for prop in dir(bpy.types.Scene):
        if prop.startswith("link_"):
            delattr(bpy.types.Scene, prop)



def update_scene_properties(scene):
    clear_link_properties()

    # Stop early if we can't determine an episode directory (no numeric segment found)
    ep_dir = find_dir_ep(bpy.data.filepath)
    if not ep_dir:
        # Remove any stale UI mapping so the panel won't appear
        if "link_casted_candidates" in scene.keys():
            del scene["link_casted_candidates"]
        return

    candidates = find_file(match_shot())

    for path in candidates:
        name = os.path.basename(path).replace(".blend", "")
        prop_name = f"link_{name}"

        setattr(
            bpy.types.Scene,
            prop_name,
            bpy.props.BoolProperty(
                name=name,
                default=True
            )
        )
