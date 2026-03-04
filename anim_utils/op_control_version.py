import bpy
import os
import json


# ------------------------------------------------
# Utils
# ------------------------------------------------


def read_log_entries(filepath):
    """
    Retourne une liste de tuples :
    (version, comment, date)
    Prefers log.json, falls back to log.txt for backwards compatibility.
    """
    if not filepath:
        return []

    directory = os.path.dirname(filepath)
    json_path = os.path.join(directory, "log.json")
    txt_path = os.path.join(directory, "log.txt")

    entries = []

    # Try JSON first
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for e in data:
                        version = e.get("version", "v00")
                        comment = e.get("comment", "") or "N/A"
                        date = e.get("timestamp", "")
                        entries.append((version, comment, date))
                    return entries
        except Exception:
            pass

    # Fallback to old text log format
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
        except Exception:
            return []

        for v, line in enumerate(lines):
            try:
                date_part, rest = line.split("]", 1)
                date = date_part.strip("[ ")
                rest = rest.strip()
                parts = rest.split(" ", 2)
                version = parts[0] if parts else f"v{v:02d}"
                comment = ""
                if "Comment:" in rest:
                    comment = rest.split("Comment:", 1)[1].strip()
                if comment == "":
                    comment = "N/A"
                entries.append((version, comment, date))
            except Exception:
                continue

    return entries



def draw_save_comment_section(layout, context):
    layout.separator()
    layout.label(text="Nouveau commentaire :")

    layout.prop(context.scene, "save_comment", text="")

    layout.operator_context = 'EXEC_DEFAULT'
    layout.operator(
        "wm.save_mainfile_incremental",
        text="Save Incremental",
        icon='FILE_TICK'
    )

# ------------------------------------------------
# Panel
# ------------------------------------------------

class VIEW3D_PT_control_version_info(bpy.types.Panel):
    bl_label = "Version Control Info"
    bl_idname = "VIEW3D_PT_control_version_info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Version Control Info"
    
    bpy.types.Scene.save_comment = bpy.props.StringProperty(
        name="Commentaire",
        description="Commentaire pour le save incrémental",
        default=""
    )


    def draw(self, context):
        layout = self.layout
        filepath = bpy.data.filepath

        entries = read_log_entries(filepath)

        if not entries:
            layout.label(text="Aucune entrée de log", icon='INFO')
            draw_save_comment_section(layout, context)
            return

        # --- Header ---
        box = layout.box()
        header = box.row(align=True)
        header.label(text="Version")
        header.label(text="Comment")
        header.label(text="Date")

        sub_box = box.box()

        # --- Rows ---
        for version, comment, date in entries:
            row = sub_box.row(align=True)
            row.label(text=version)
            row.label(text=comment)
            row.label(text=date)

        # --- Save section ---
        draw_save_comment_section(layout, context)


# ------------------------------------------------
# Register
# ------------------------------------------------

classes = (VIEW3D_PT_control_version_info,)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)