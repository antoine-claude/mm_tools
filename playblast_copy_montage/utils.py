import os
import bpy



def get_ep_from_blend():
    blend_name = bpy.path.basename(bpy.data.filepath)
    parts = blend_name.split("_")
    return parts[1] if len(parts) > 1 else "UNKNOWN"


def get_playblast_source_file(scene):
    """
    Retourne le chemin ABSOLU du playblast (.mov)
    ou None s'il n'existe pas
    """
    base_path = bpy.path.abspath(scene.render.filepath)

    # force .mov si pas d'extension
    if not os.path.splitext(base_path)[1]:
        base_path += ".mov"

    source_file = os.path.abspath(base_path)

    if not os.path.isfile(source_file):
        return None

    return source_file


def get_playblast_dest_file(scene):
    """
    Retourne le chemin FINAL de destination (même si le fichier n'existe pas encore)
    """
    base_dest = bpy.path.abspath(scene.copy_output.copy_output_path)
    ep = get_ep_from_blend()
    layer = scene.copy_output.copy_output_layer

    filename = os.path.basename(
        bpy.path.abspath(scene.render.filepath)
    )
    if not filename.endswith(".mov"):
        filename += ".mov"
    new_copy_path = os.path.join(base_dest,ep,f"EP{ep}_{layer}",filename)
    if not "UNKNOWN" in new_copy_path :

        return os.path.abspath(new_copy_path)
    else :
        return None


def remap_output_path(scene):
    blend_path = bpy.data.filepath
    blend_name = os.path.splitext(os.path.basename(blend_path))[0]
    parts = blend_name.split("_")[:-3]
    for i, part in enumerate(parts) :
        if part == "001" :
            parts[i]="" 
    
    merge_parts = "_".join(filter(None,parts))
    

    dir_name = os.path.basename(os.path.dirname(blend_path))
    if dir_name == "Layout" :
        scene.render.filepath = os.path.join(os.path.dirname(blend_path), f"{merge_parts}_LAY.mov")
        return os.path.join(os.path.dirname(blend_path), f"{merge_parts}_LAY.mov")
    
    elif dir_name == "Animation_Spline":
        parts_anim = blend_name.split("_")[:-1]
        for i, part in enumerate(parts_anim) :
            if part == "001" :
                parts_anim[i]="" 
        merge_parts_anim = "_".join(filter(None,parts))
        scene.render.filepath = os.path.join(os.path.dirname(blend_path), f"{merge_parts_anim}.mov")
        return os.path.join(os.path.dirname(blend_path), f"{merge_parts_anim}.mov")
    
    if dir_name == "Animation_Stopmo" :
        scene.render.filepath = os.path.join(os.path.dirname(blend_path), f"{merge_parts}_SPL.mov")
        return os.path.join(os.path.dirname(blend_path), f"{merge_parts}_SPL.mov")
    

    else:
        return None
