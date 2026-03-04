import bpy
from .utils import get_playblast_dest_file


class PLAYBLAST_PT_duplicate_panel(bpy.types.Panel):
    bl_label = "Duplication FFmpeg"
    bl_idname = "PLAYBLAST_PT_duplicate_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("playblast.remap_output_path")
        layout.operator("render.opengl").animation = True

        layout.prop(scene.copy_output, "copy_output_path")
        layout.prop(scene.copy_output, "copy_output_layer")

        dest_file = get_playblast_dest_file(scene)
        if not dest_file :
            dest_file = "Chemin du shot introuvable"
        layout.label(
            text=f"Chemin final de la copie : {dest_file}",
            icon='FILE_FOLDER'
        )

        layout.operator(
            "playblast.duplicate_ffmpeg",
            icon='DUPLICATE'
        )

        # row = layout.row(align=True)
        layout.operator("wm.open_copy_output_path", icon='FILE_FOLDER')

classes = (PLAYBLAST_PT_duplicate_panel,
           )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)