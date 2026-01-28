import re
import bpy

from bpy.types import Operator
from bpy.props import BoolProperty
from .utils import remap_drivers, remove_animation_on_ctrl_objects, clean_chara_name, replace_from_list, remap_parents

# -------------------------------------------------------------------
# OPERATOR 1 : MODIFY RENDER PATHS (COMPOSITING / ALL SCENES)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# OPERATOR : DUPLICATE COLLECTIONS
# -------------------------------------------------------------------

class LIGHTING_OT_duplicate_light_cols(Operator):
    bl_idname = "lighting.duplicate_light_cols"
    bl_label = "Duplicate Light Collections"
    bl_options = {'REGISTER', 'UNDO'}

    linked: BoolProperty(default=False)

    def execute(self, context):
        light_col = bpy.data.collections.get("Light_CH")
        if not light_col or not light_col.children:
            self.report({'ERROR'}, "Light_CH missing or empty")
            return {'CANCELLED'}

        base = light_col.children[0]

        for c in list(light_col.children)[1:]:
            bpy.data.collections.remove(c)

        chara_col = bpy.data.collections.get("Chara")
        for chara in chara_col.children[1:]:
            dupe_lut = {}
            new_col = bpy.data.collections.new(base.name)
            light_col.children.link(new_col)

            def recurse(src, dst):
                for obj in src.objects:
                    dup = obj.copy()
                    if obj.data:
                        dup.data = obj.data.copy()
                    dst.objects.link(dup)
                    dupe_lut[obj] = dup
                for child in src.children:
                    cc = bpy.data.collections.new(child.name)
                    dst.children.link(cc)
                    recurse(child, cc)

            recurse(base, new_col)
            remap_drivers(dupe_lut)
            remap_parents(dupe_lut)

        return {'FINISHED'}


# -------------------------------------------------------------------
# OPERATOR : RENAME COLLECTIONS / OBJECTS
# -------------------------------------------------------------------

class LIGHTING_OT_rename_light_cols(Operator):
    bl_idname = "lighting.rename_light_cols"
    bl_label = "Rename Light Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        chara_col = bpy.data.collections.get("Chara")
        light_col = bpy.data.collections.get("Light_CH")

        to_replace = ["xxx", "MM_CHR_CHARA"]
        to_replace += [c.name for c in chara_col.children]

        for i, col in enumerate(light_col.children):
            chara = chara_col.children[i]
            cname = clean_chara_name(chara.name)
#            if not cname in col.name:
            col.name = replace_from_list(col.name, to_replace, cname)

            for sub in col.children_recursive:
                sub.name = replace_from_list(sub.name, to_replace, cname)

            for obj in col.all_objects:
                obj.name = replace_from_list(obj.name, to_replace, cname)
                if obj.data:
                    obj.data.name = replace_from_list(obj.data.name, to_replace, cname)
                for constraint in obj.constraints:
                    constraint.name = replace_from_list(constraint.name, to_replace, cname)
                    if constraint.type == "LOCKED_TRACK" and obj.name.endswith("RimKicker_Ctrl"):
                        print("constraint name", constraint.type)
                        print("chara.name+_Lit_Loc", chara.name+"_Lit_Loc", bpy.data.objects.get(chara.name+"_Lit_Loc") )
                        constraint.target = bpy.data.objects.get(chara.name+"_Lit_Loc")
                    elif obj.name.endswith("LightRig_Ctrl"):
                        constraint.target = bpy.data.objects.get(cname+"_LightRig_Ctrl")
                    #check constraint target replace from list 
                    elif obj.name.endswith("RimKicker_Ctrl") and constraint.type != "LOCKED_TRACK":
                        constraint.target = bpy.data.objects["Render_Cam"]
                    else :
                        constraint.target = bpy.data.objects.get(replace_from_list(constraint.target.name, to_replace, cname))

                remove_animation_on_ctrl_objects(col)

        return {'FINISHED'}



# -------------------------------------------------------------------
# OPERATOR : LIGHT LINKING RECEIVER
# -------------------------------------------------------------------

class LIGHTING_OT_light_linking_receiver(Operator):
    bl_idname = "lighting.setup_light_linking"
    bl_label = "Setup Light Linking"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        chara_col = bpy.data.collections.get("Chara")
        light_col = bpy.data.collections.get("Light_CH")

        for i, col in enumerate(light_col.children):
            chara = chara_col.children[i]
            cname = clean_chara_name(chara.name)
            if not cname in col.name :
                continue
            for obj in col.all_objects :
                if obj.type == "LIGHT" :
                    if obj.name.endswith("LS_Rim_Sun") or obj.name.endswith("RS_Key_Sun"):
                        if not bpy.data.collections.get(f"Light Linking for {obj.name}") :
                            light_linking_col = bpy.data.collections.new(f"Light Linking for {obj.name}")
                        else :
                            light_linking_col = bpy.data.collections.get(f"Light Linking for {obj.name}")
                        obj.light_linking.receiver_collection = light_linking_col
                        for chara in chara_col.children:
                            if clean_chara_name(chara.name) == cname:
                                if chara.name not in light_linking_col.children :
                                    light_linking_col.children.link(bpy.data.collections[chara.name])

        return {'FINISHED'}

# -------------------------------------------------------------------
# OPERATOR : MODIFY RENDER PATHS
# -------------------------------------------------------------------

class LIGHTING_OT_modify_render_paths(Operator):
    bl_idname = "lighting.modify_render_paths"
    bl_label = "Modify Render Paths (All Scenes)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        name = bpy.path.basename(bpy.data.filepath)
        try:
            a, b, c = name.split("_")[1:4]
        except Exception:
            self.report({'ERROR'}, "Invalid blend name")
            return {'CANCELLED'}

        for scene in bpy.data.scenes:
            scene.render.filepath = scene.render.filepath.replace(scene.render.filepath.split("/")[3], a)

        return {'FINISHED'}




# -------------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------------

classes = (
    LIGHTING_OT_duplicate_light_cols,
    LIGHTING_OT_rename_light_cols,
    LIGHTING_OT_light_linking_receiver,
    LIGHTING_OT_modify_render_paths,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
