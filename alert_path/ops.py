import bpy
from bpy.app.handlers import persistent

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
TARGET_PATH = "R:\\melodyandmomon"

# --------------------------------------------------
# POPUP OPERATOR
# --------------------------------------------------
class CHECKPATH_OT_show_popup(bpy.types.Operator):
    bl_idname = "wm.check_project_path_popup"
    bl_label = "Chemin incorrect"

    message: bpy.props.StringProperty()

    def invoke(self, context, event=None):
        lines = self.message.split("\n")

        def draw(menu_self, context):
            for line in lines:
                menu_self.layout.label(text=line)

        context.window_manager.popup_menu(
            draw,
            title="Avertissement",
            icon="ERROR"
        )
        return {'FINISHED'}

# --------------------------------------------------
# PATH CHECK LOGIC
# --------------------------------------------------
def run_path_check():
    filepath = bpy.data.filepath
    filename = bpy.path.basename(filepath)

    # Fichier non enregistré
    if not filepath:
        bpy.ops.wm.check_project_path_popup(
            "INVOKE_DEFAULT",
            message="Le fichier n'a pas encore été enregistré !"
        )
        return

    # Mauvais chemin + nom commençant par MM_
    if not filepath.startswith(TARGET_PATH) and filename.startswith("MM_"):
        bpy.ops.wm.check_project_path_popup(
            "INVOKE_DEFAULT",
            message=(
                f"Le fichier n'est pas dans : {TARGET_PATH}\n"
                f"Chemin actuel : {filepath}"
            )
        )

# --------------------------------------------------
# HANDLER load_post
# --------------------------------------------------
@persistent
def check_project_path(dummy):
    print("[CHECKPATH] load_post déclenché")
    run_path_check()

def ensure_alert_handlers():
    if check_project_path not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(check_project_path)

def remove_alert_handlers():
    if check_project_path in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(check_project_path)

# --------------------------------------------------
# REGISTER / UNREGISTER
# --------------------------------------------------
def register():
    bpy.utils.register_class(CHECKPATH_OT_show_popup)
    ensure_alert_handlers()

def unregister():
    bpy.utils.unregister_class(CHECKPATH_OT_show_popup)
    remove_alert_handlers()
