import bpy

# --------------------------------------------------------------------
# UI Panel
# --------------------------------------------------------------------

class VIEW3D_PT_frustum_visibility(bpy.types.Panel):
    bl_label = "Camera Frustum Visibility"
    bl_category = "FrustumVis"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.label(text="Active Camera:")
        col.prop(scene, "camera", text="")

        col.separator()
        col.operator("frustumvis.update_visibility", icon='RESTRICT_VIEW_OFF')

        col.separator()
        row = col.row(align=True)
        row.prop(scene.frustum_vis_props, "frustum_vis_auto_update", text="Auto-update")
        row.operator("frustumvis.toggle_auto_update", text="", icon='REC')

        col.separator()
        col.prop(scene.frustum_vis_props, "frustum_vis_margin")
        col.prop(scene.frustum_vis_props, "frustum_vis_only_mesh")
        col.prop(scene.frustum_vis_props, "frustum_vis_collection")
        col.prop(scene.frustum_vis_props, "frustum_vis_frame_step")

classes = (VIEW3D_PT_frustum_visibility,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)