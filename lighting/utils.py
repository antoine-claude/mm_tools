import re
import bpy
# -------------------------------------------------------------------
# UTILS
# -------------------------------------------------------------------

def remove_blender_suffix(name):
    return re.sub(r"\.\d{3}$", "", name)


def clean_chara_name(name):
    return re.sub(r"_[A-Z]_[A-Z]$", "", name)


def replace_from_list(text, to_replace, new_value):
    text = remove_blender_suffix(text)
    text = re.sub(r"MM_CHR_[^_\.]+", new_value, text)
    for elt in to_replace:
        if elt in text:
            text = text.replace(elt, new_value)
            break
    return remove_blender_suffix(text)


def replace_chara_tokens(name, to_replace, chara):
    if not name:
        return name

    name = remove_blender_suffix(name)

    target_full = chara.name                     # MM_CHR_GenericGirl02_A_A
    target_clean = clean_chara_name(chara.name)  # MM_CHR_GenericGirl02

    # Si le bon chara FULL est déjà présent → on ne fait rien
    if target_full in name:
        return name

    #Nettoyage : enlever tout suffixe _A_A / _B_C existant
    name = re.sub(r"_[A-Z]_[A-Z](?=\.|$)", "", name)

    #Remplacement prioritaire sur clean target
    if target_clean in name:
        name = name.replace(target_clean, target_full)
        print("name", name)
        return remove_blender_suffix(name)

    #Remplacement via la liste des anciens charas
    for token in to_replace:
        token_clean = clean_chara_name(token)

        if token in name:
            name = name.replace(token, target_full)
            break

        if token_clean in name:
            name = name.replace(token_clean, target_full)
            break

    return remove_blender_suffix(name)


def remove_animation_on_ctrl_objects(collection):
    for obj in collection.all_objects:
        if obj.name.endswith("Ctrl") and obj.animation_data:
            # remove animation exept drivers
            # Remove all animation data except drivers
            if obj.animation_data.action:
                # Iterate over all f-curves
                for fcurve in obj.animation_data.action.fcurves:
                    # Clear keyframes but keep drivers
                    if not fcurve.driver:
                        fcurve.keyframe_points.clear()
                # Update the animation data
                obj.animation_data.action.update()


def remap_drivers(dupe_lut):
    for dup in dupe_lut.values():
        ad = dup.animation_data
        if not ad:
            continue
        for fc in ad.drivers:
            for var in fc.driver.variables:
                for tgt in var.targets:
                    if tgt.id in dupe_lut:
                        tgt.id = dupe_lut[tgt.id]
        ad_data = dup.data.animation_data
        if not ad_data:
            continue
        for fc in ad_data.drivers:
            for var in fc.driver.variables:
                for tgt in var.targets:
                    if tgt.id in dupe_lut:
                        tgt.id = dupe_lut[tgt.id]


#select and remap relations parent and keep transform 
def remap_parents(dupe_lut):
    for dup in dupe_lut.values():
        if dup.parent and dup.parent in dupe_lut:
            old_matrix = dup.matrix_world.copy()
            dup.parent = dupe_lut[dup.parent]
            dup.matrix_world = old_matrix

def delete_collection(col):
    # Supprimer les objets (une seule fois)
    for obj in list(col.all_objects):
        if obj.type == "MESH":
            bpy.data.meshes.remove(obj.data, do_unlink=True) if obj.data else None
        elif obj.type == "LIGHT" :
            bpy.data.lights.remove(obj.data, do_unlink=True) if obj.data else None
        else :
            bpy.data.objects.remove(obj, do_unlink=True)

    # Supprimer les sous-collections (bottom-up)
    for sub in list(col.children_recursive):
        bpy.data.collections.remove(sub, do_unlink=True)

    bpy.data.collections.remove(col, do_unlink=True)

            