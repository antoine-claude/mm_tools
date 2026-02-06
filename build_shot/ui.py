import bpy

class VIEW3D_PT_AnimationFoldersPanel(bpy.types.Panel):
    bl_label = "Animation Folders"
    bl_idname = "ANIMATION_FOLDERS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation Builder"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        layout.operator("animation.create_blocking_file")
        layout.operator("animation.create_anime_next_step")

class VIEW3D_PT_LayoutBuilderPanel(bpy.types.Panel):
    bl_label = "Layout Shot Builder"
    bl_idname = "LAYOUT_BUILDER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation Builder"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        layout.operator("layout.build_next_layout_shot")   

classes = (VIEW3D_PT_AnimationFoldersPanel,
           VIEW3D_PT_LayoutBuilderPanel,
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)