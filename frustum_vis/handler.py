import bpy
from .core import update_visibility_from_camera

# --------------------------------------------------------------------
# Frame handler
# --------------------------------------------------------------------

def frustum_vis_frame_handler(scene):
    if not scene.frustum_vis_auto_update:
        return

    step = max(scene.frustum_vis_frame_step, 1)
    if scene.frame_current % step != 0:
        return

    update_visibility_from_camera(scene)


def ensure_frustum_handler():
    if frustum_vis_frame_handler not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(frustum_vis_frame_handler)


def remove_frustum_handler():
    if frustum_vis_frame_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(frustum_vis_frame_handler)
