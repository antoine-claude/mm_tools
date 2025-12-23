import bpy
import os
import shutil
from datetime import datetime
import ctypes
import json

# -----------------------------------------
# Fonctions utilitaires
# -----------------------------------------

def purge_unused_data():
    bpy.ops.outliner.orphans_purge(do_recursive=True)

def increment_number(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    parsed = name.split('_')


    # gestion vXX
    if len(parsed) > 1 and parsed[-2].startswith("v"):
        current_version = int(parsed[-2][1:])
        new_version = current_version + 1
        parsed[-2] = f"v{new_version:02d}"

    return parsed, ext

def save_with_incremental(filepath=None):
    purge_unused_data()
    bpy.ops.file.make_paths_absolute()

    if filepath is None:
        filepath = bpy.data.filepath
    if not filepath:
        print("No file path specified for saving.")
        return

    parsed, ext = increment_number(filepath)

    new_name = '_'.join(parsed) + ext
    new_filepath = os.path.join(os.path.dirname(filepath), new_name)

    # Check free disk space before saving (require at least 10 MB)
    try:
        free_bytes = shutil.disk_usage(os.path.dirname(filepath) or os.getcwd()).free
    except Exception:
        free_bytes = None

    if free_bytes is not None and free_bytes < 10 * 1024 * 1024:
        # Not enough space to save safely
        raise RuntimeError(f"Not enough disk space to save file: {free_bytes} bytes available")

    try:
        bpy.ops.wm.save_mainfile(filepath=new_filepath)
    except Exception as e:
        # propagate exception to caller so operator can report and log it
        raise

    print(f"Saved main file bordel de merde: {new_filepath}")
    return new_filepath

def get_log_json_path(filepath):
    directory = os.path.dirname(filepath)
    return os.path.join(directory, "log.json")

def load_log_entries_json(filepath):
    path = get_log_json_path(filepath)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        return []
    return []

def write_log(filepath, version, comment):
    """
    Append an entry to log.json:
    { "timestamp": "...", "version": "v02", "comment": "..." }
    """
    if not filepath:
        return

    directory = os.path.dirname(filepath)
    log_path = get_log_json_path(filepath)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        os.makedirs(directory, exist_ok=True)
    except Exception:
        return

    try:
        entries = load_log_entries_json(filepath)
        entries.append({
            "timestamp": timestamp,
            "version": version,
            "comment": comment or ""
        })

        # Make existing file writable
        if os.path.exists(log_path):
            os.chmod(log_path, 0o644)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

        # Make file read-only after writing
        os.chmod(log_path, 0o444)
    except Exception:
        pass

def show_message(context, message, title="Info", icon='INFO'):
    """Show a modal popup message using Blender's popup_menu."""
    def draw(self, _context):
        self.layout.label(text=message)
    context.window_manager.popup_menu(draw, title=title, icon=icon)


# -----------------------------------------
# Les Operators
# -----------------------------------------

class WM_OT_save_mainfile_incremental(bpy.types.Operator):
    bl_idname = "wm.save_mainfile_incremental"
    bl_label = "Save Incremental"

    # utilisé UNIQUEMENT pour le popup
    comment: bpy.props.StringProperty(
        name="Commentaire",
        description="Commentaire pour le log",
        default=""
    )

    _invoked = False

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "comment")

    def invoke(self, context, event):
        # appel classique → popup
        self._invoked = True
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "No file path defined.")
            return {'CANCELLED'}

        # --- Choix de la source du commentaire ---
        if self._invoked:
            # popup
            comment = self.comment
        else:
            # panel
            comment = context.scene.save_comment

        # --- Log + Save ---
        new_filepath = save_with_incremental(filepath)
        parsed, _ = increment_number(filepath)

        # If filename doesn't contain vXX, infer next version from JSON log
        if not parsed[-2].startswith("v"):
            last_version = "v01"
            entries = load_log_entries_json(filepath)
            if entries:
                try:
                    last_entry = entries[-1]
                    version_str = last_entry.get("version", "")
                    if version_str.startswith("v"):
                        current_version = int(version_str[1:])
                        last_version = f"v{current_version + 1:02d}"
                except Exception:
                    pass
            parsed[-2] = last_version

        # Write JSON log entry (version, comment)
        write_log(new_filepath, parsed[-2], comment)

        # nettoyage
        comment = ""
        self.comment = ""
        context.scene.save_comment = ""

        return {'FINISHED'}



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
