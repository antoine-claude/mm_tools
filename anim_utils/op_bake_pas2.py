import bpy

# --- Définition de l'opérateur ---
class OBJECT_OT_bake_pas2(bpy.types.Operator):
    bl_idname = "view3d.mm_bake_pas2"
    bl_label = "Bake Pas de 2"
    bl_description = "Bake l'action sur l'armature en pas de 2"
    bl_options = {'REGISTER', 'UNDO'}

    # --- Propriétés de l’opérateur ---
    only_selected: bpy.props.BoolProperty(
        name="only_selected",
        description="Bake seulement l'armature selectionné",
        default=True
    )
    message: bpy.props.StringProperty(
    name="Message",
    default="Aucune armature selectionné !"
    )

    # --- Condition d'exécution ---
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'ARMATURE'

    # --- Exécution ---
    def execute(self, context):
        obj = context.active_object
        if obj.type == "ARMATURE" :
            self.report({'INFO'}, f"{self.message} (Armature: {obj.name})")
            print(f"{self.message} (Armature: {obj.name})")
            
        self.report({'INFO'}, "Bake action en pas de 2 !")
        

        if not self.only_selected:
            objects = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
        else:
            obj = bpy.context.active_object
            objects = [obj for obj in bpy.context.selected_objects if obj.type == "ARMATURE"]
            
        for object in objects :
            object.select_set(True)
            
            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end
            step = 2

            bpy.ops.nla.bake(frame_start=frame_start, frame_end=frame_end, step = step, only_selected = False, bake_types={'POSE'})

            fcurves = object.animation_data.action.fcurves
            for fcurve in fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'CONSTANT'
            object.select_set(False)
                    
        return {'FINISHED'}


# --- Fonction de dessin dans le menu Object ---
classes = [OBJECT_OT_bake_pas2]
