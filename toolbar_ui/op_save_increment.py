import bpy
import os

# -----------------------------------------
# Fonctions utilitaires
# -----------------------------------------

def purge_unused_data():
    bpy.ops.outliner.orphans_purge(do_recursive=True)


def save_with_incremental(filepath=None):
    purge_unused_data()
    bpy.ops.file.make_paths_absolute()

    if filepath is None:
        filepath = bpy.data.filepath
    if not filepath:
        print("No file path specified for saving.")
        return

    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    parsed = name.split('_')

    # gestion vXX
    if len(parsed) > 1 and parsed[-2].startswith("v"):
        current_version = int(parsed[-2][1:])
        new_version = current_version + 1
        parsed[-2] = f"v{new_version:02d}"
    else:
        parsed.insert(-1, "v01")

    new_name = '_'.join(parsed) + ext
    new_filepath = os.path.join(os.path.dirname(filepath), new_name)

    bpy.ops.wm.save_mainfile(filepath=new_filepath)
    print(f"Saved main file: {new_filepath}")


# -----------------------------------------
# Les Operators
# -----------------------------------------

class WM_OT_save_mainfile_incremental(bpy.types.Operator):
    bl_idname = "wm.save_mainfile_incremental"
    bl_label = "Save Incremental"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={'SKIP_SAVE'})

    def execute(self, context):
        filepath = self.filepath if self.filepath else bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "No file path defined.")
            return {'CANCELLED'}

        save_with_incremental(filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = bpy.data.filepath
        return self.execute(context)


class WM_OT_save_mainfile_with_absolute_paths(bpy.types.Operator):
    bl_idname = "wm.save_mainfile_with_absolute_paths"
    bl_label = "Save with Absolute Paths"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={'SKIP_SAVE'})

    def execute(self, context):
        filepath = self.filepath if self.filepath else bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "No file path defined.")
            return {'CANCELLED'}

        bpy.ops.file.make_paths_absolute()
        bpy.ops.wm.save_mainfile(filepath=filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = bpy.data.filepath
        return self.execute(context)


# -----------------------------------------
# Liste des classes exportables
# -----------------------------------------

classes = [
    WM_OT_save_mainfile_incremental,
    WM_OT_save_mainfile_with_absolute_paths,
]
