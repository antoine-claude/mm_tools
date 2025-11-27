import bpy

# --------------------------------------------------------------------
# Scene properties
# --------------------------------------------------------------------

def register_frustum_properties():
    scene = bpy.types.Scene

    scene.frustum_vis_margin = bpy.props.FloatProperty(
        name="Frustum Margin",
        default=0.05,
        min=0.0,
        max=1.0,
        description="Extra margin around camera frame"
    )

    scene.frustum_vis_auto_update = bpy.props.BoolProperty(
        name="Auto-update",
        default=False,
        description="Visibility auto-update on frame change"
    )

    scene.frustum_vis_only_mesh = bpy.props.BoolProperty(
        name="Only Mesh",
        default=True,
        description="Process only Mesh objects"
    )

    scene.frustum_vis_collection = bpy.props.PointerProperty(
        name="Restrict Collection",
        type=bpy.types.Collection,
        description="Restrict to this collection (recursive)"
    )

    scene.frustum_vis_frame_step = bpy.props.IntProperty(
        name="Frame Step",
        default=1,
        min=1,
        max=50,
        description="Update every N frames"
    )


def unregister_frustum_properties():
    scene = bpy.types.Scene
    del scene.frustum_vis_margin
    del scene.frustum_vis_auto_update
    del scene.frustum_vis_only_mesh
    del scene.frustum_vis_collection
    del scene.frustum_vis_frame_step
