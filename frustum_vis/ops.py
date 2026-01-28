import bpy
from .core import update_visibility_from_camera


def frustum_vis_frame_handler(scene):
    if not scene.frustum_vis_auto_update:
        return

    step = max(scene.frustum_vis_frame_step, 1)
    if scene.frame_current % step != 0:
        return

    update_visibility_from_camera(scene)




def ensure_frustum_handler():
    handlers = bpy.app.handlers.frame_change_post
    if frustum_vis_frame_handler not in handlers:
        handlers.append(frustum_vis_frame_handler)


# --------------------------------------------------------------------
# Operators
# --------------------------------------------------------------------

class FRUSTUMVIS_OT_update(bpy.types.Operator):
    """Update object visibility based on camera frustum"""
    bl_idname = "frustumvis.update_visibility"
    bl_label = "Update Visibility"

    def execute(self, context):
        update_visibility_from_camera(context.scene)
        return {'FINISHED'}


class FRUSTUMVIS_OT_toggle_auto(bpy.types.Operator):
    """Toggle automatic update on frame change"""
    bl_idname = "frustumvis.toggle_auto_update"
    bl_label = "Toggle Auto-Update"  

    def execute(self, context):
        scene = context.scene
        scene.frustum_vis_auto_update = not scene.frustum_vis_auto_update

        if scene.frustum_vis_auto_update:
            ensure_frustum_handler()
            self.report({'INFO'}, "Auto-update ENABLED")
        else:
            self.report({'INFO'}, "Auto-update DISABLED")

        return {'FINISHED'}


classes = (FRUSTUMVIS_OT_update,FRUSTUMVIS_OT_toggle_auto,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.frame_change_post.append(frustum_vis_frame_handler)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.frame_change_post.remove(frustum_vis_frame_handler)