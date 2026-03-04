import bpy

# --------------------------------------------------------------------
# Scene properties
# --------------------------------------------------------------------
class FRUSTUM_property_group_panel(bpy.types.PropertyGroup):
    """Group of properties for Frustum Visibility addon"""

    frustum_vis_margin: bpy.props.FloatProperty(
        name="Frustum Margin",
        default=0.05,
        min=0.0,
        max=1.0,
        description="Extra margin around camera frame"
    )

    frustum_vis_auto_update: bpy.props.BoolProperty(
        name="Auto-update",
        default=False,
        description="Visibility auto-update on frame change"
    )

    frustum_vis_only_mesh: bpy.props.BoolProperty(
        name="Only Mesh",
        default=True,
        description="Process only Mesh objects"
    )

    frustum_vis_collection: bpy.props.PointerProperty(
        name="Restrict Collection",
        type=bpy.types.Collection,
        description="Restrict to this collection (recursive)"
    )

    frustum_vis_frame_step: bpy.props.IntProperty(
        name="Frame Step",
        default=1,
        min=1,
        max=50,
        description="Update every N frames"
    )



classes = (FRUSTUM_property_group_panel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.frustum_vis_props = bpy.props.PointerProperty(type=FRUSTUM_property_group_panel)

def unregister():
    del bpy.types.Scene.frustum_vis_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)