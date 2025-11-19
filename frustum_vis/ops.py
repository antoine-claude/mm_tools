import bpy
from .core import update_visibility_from_camera
from .handler import ensure_handler

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
            ensure_handler()
            self.report({'INFO'}, "Auto-update ENABLED")
        else:
            self.report({'INFO'}, "Auto-update DISABLED")

        return {'FINISHED'}


def get_classes():
    return (
        FRUSTUMVIS_OT_update,
        FRUSTUMVIS_OT_toggle_auto,
    )
