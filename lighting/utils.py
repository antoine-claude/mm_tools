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


def remove_animation_on_ctrl_objects(collection):
    for obj in collection.all_objects:
        if obj.name.endswith("Ctrl") and obj.animation_data:
            obj.animation_data_clear()


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

#remap relations parent and keep transform
def remap_parents(dupe_lut):
    for dup in dupe_lut.values():
        if dup.parent and dup.parent in dupe_lut:
            old_matrix = dup.matrix_world.copy()
            dup.parent = dupe_lut[dup.parent]
            dup.matrix_world = old_matrix