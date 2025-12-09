import bpy
from bpy.app.handlers import persistent

TARGET_PATH = "R:\\melodyandmomon"

def run_path_check():
    filepath = bpy.data.filepath
    filename = bpy.path.basename(bpy.data.filepath)

    if not filepath:
        bpy.ops.wm.check_project_path_popup(
            'INVOKE_DEFAULT',
            message="Le fichier n'a pas encore été enregistré !"
        )
        return

    if not filepath.startswith(TARGET_PATH) or not filename.startswith("MM_"):
        bpy.ops.wm.check_project_path_popup(
            'INVOKE_DEFAULT',
            message=(
                f"Le fichier n'est pas dans : {TARGET_PATH}\n"
                f"Le chemin actuel : {filepath}"
            )
        )


# ----------------------------------------------------------------
# Handler load_post
# ----------------------------------------------------------------
@persistent
def check_project_path(dummy):
    print("[CHECKPATH] Handler load_post OK")
    run_path_check()

def ensure_alert_handlers():
    if check_project_path not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(check_project_path)


def remove_alert_handlers():
    if check_project_path in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(check_project_path)
