import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

from .utils import clean_chara_name, replace_chara_tokens, remove_animation_on_ctrl_objects, remap_drivers, delete_collection

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
            delete_collection(c)

            # -------- objects --------

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
            remap_parents(dupe_lut)
            remap_drivers(dupe_lut)
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

        if not chara_col or not light_col:
            self.report({'ERROR'}, "Missing Chara or Light_CH collection")
            return {'CANCELLED'}
        to_replace = ["xxx", "MM_CHR_CHARA"]
        to_replace += [c.name for c in chara_col.children]
        print("to replace", to_replace)

        for i, col in enumerate(light_col.children):
            if '_'.join(col.name.split("_")[:3]) not in to_replace :
                to_replace.append("_".join(col.name.split("_")[:3]))
            #     print("'_'.join(col.name.split('_')[:3])", '_'.join(col.name.split("_")[:3]))
            if i >= len(chara_col.children):
                continue
            col_obj = []
            chara = chara_col.children[i]
            rename = lambda n: replace_chara_tokens(n, to_replace, chara)

            # -------- collections --------
            print(rename(col.name), "rename(col.name)")
            col.name = rename(col.name)
            for sub in col.children_recursive:
                sub.name = rename(sub.name)

            # -------- objects --------
            for obj in col.all_objects:
                obj.name = rename(obj.name)
                col_obj.append(obj)
                if obj.data:
                    obj.data.name = rename(obj.data.name)

                # --- constraints creation ---
                if obj.name.endswith("RimKicker_Ctrl"):
                    if not any(c.type == 'COPY_LOCATION' for c in obj.constraints):
                        c = obj.constraints.new("COPY_LOCATION")
                        c.name = chara.name + "_Copy Location"

                    if not any(c.type == 'COPY_ROTATION' for c in obj.constraints):
                        c = obj.constraints.new("COPY_ROTATION")
                        c.name = chara.name + "_Copy Rotation"

                    if not any(c.type == 'LOCKED_TRACK' for c in obj.constraints):
                        c = obj.constraints.new("LOCKED_TRACK")
                        c.name = chara.name + "_Locked Track"

                elif obj.name.endswith("LightRig_Ctrl"):
                    if not any(c.type == 'COPY_LOCATION' for c in obj.constraints):
                        c = obj.constraints.new("COPY_LOCATION")
                        c.name = chara.name + "_Copy Location"

                # --- constraints setup ---
                for constraint in obj.constraints:
                    if constraint.type == "LOCKED_TRACK" and obj.name.endswith("RimKicker_Ctrl"):
                        constraint.target = bpy.data.objects.get("Render_Cam")
                        constraint.track_axis = "TRACK_X"
                        constraint.lock_axis = "LOCK_Z"

                    elif obj.name.endswith("RimKicker_Ctrl"):
                        constraint.target = bpy.data.objects.get(
                            f"{chara.name}_LightRig_Ctrl"
                        )

                        if constraint.type == "COPY_LOCATION":
                            constraint.use_offset = True

                        elif constraint.type == "COPY_ROTATION":
                            constraint.use_x = False
                            constraint.use_y = False
                            constraint.use_z = True
                            constraint.mix_mode = "BEFORE"

                    elif obj.name.endswith("LightRig_Ctrl"):
                        constraint.target = bpy.data.objects.get(
                            f"{chara.name}_Lit_Loc"
                        )
                        obj["Turn Kicker Off/On"] = True

                    elif not constraint.type == "LOCKED_TRACK" and not obj.name.endswith("RimKicker_Ctrl"):                    
                        constraint.target = bpy.data.objects.get(rename(constraint.target.name))
                        
                    constraint.name = rename(constraint.name)

            remove_animation_on_ctrl_objects(col)

        return {'FINISHED'}


class LIGHTING_OT_light_property_setter(Operator):
    bl_idname = "lighting.set_light_properties"
    bl_label = "Set Light Properties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_col = bpy.data.collections.get("Light_CH")
        if not light_col or not light_col.children:
            self.report({'ERROR'}, "Light_CH missing or empty")
            return {'CANCELLED'}

        for col in light_col.children:
            for obj in col.all_objects:
                if obj.name.endswith("RS_Key_Ctrl"):
                    bpy.data.objects[obj.name]["Key Bias"] = 0.8726646304130554
                    bpy.data.objects[obj.name]["Key Color"] = [1.0, 0.6779999732971191, 0.30000001192092896]
                    bpy.data.objects[obj.name]["Key Intensity"] = 10.0
                    
                if obj.name.endswith("LS_Rim_Ctrl"):
                    bpy.data.objects[obj.name]["Rim Bias"] = 0.3490658402442932
                    bpy.data.objects[obj.name]["Rim Color"] = [0.7749999761581421, 0.8312501311302185, 1.0]
                    bpy.data.objects[obj.name]["Rim Intensity"] = 2.0
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

classes = (LIGHTING_OT_duplicate_light_cols,
           LIGHTING_OT_rename_light_cols,
           LIGHTING_OT_light_property_setter,
           LIGHTING_OT_light_linking_receiver,
           LIGHTING_OT_modify_render_paths,
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
