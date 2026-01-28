import bpy
from .ops import run_path_check

# ------------------------------------------------------------------
# MENU dans la Topbar (contenu du menu)
# ------------------------------------------------------------------
class CHECKPATH_MT_menu(bpy.types.Menu):
    bl_label = "Alert Filepath"
    bl_idname = "CHECKPATH_MT_menu"

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.operator("wm.check_project_path_manual", icon="ERROR")
        layout.alert = False


# ------------------------------------------------------------------
# Fake operator rouge pour simuler un menu dans la Topbar
# ------------------------------------------------------------------
class CHECKPATH_OT_fake_menu(bpy.types.Operator):
    bl_idname = "wm.checkpath_fake_menu"
    bl_label = "Alert Filepath"

    def invoke(self, context, event=None):
        bpy.ops.wm.call_menu(name="CHECKPATH_MT_menu")
        return {'FINISHED'}


# ------------------------------------------------------------------
# Opérateur de vérification manuelle
# ------------------------------------------------------------------
class CHECKPATH_OT_manual_check(bpy.types.Operator):
    bl_idname = "wm.check_project_path_manual"
    bl_label = "Vérifier le chemin"

    def execute(self, context):
        run_path_check()
        return {'FINISHED'}


# ------------------------------------------------------------------
# Topbar : ajout du bouton rouge
# ------------------------------------------------------------------
def draw_alert_menu(self, context):
    TARGET_PATH = "R:\\melodyandmomon"
    filepath = bpy.data.filepath
    filename = bpy.path.basename(filepath)

    # CONDITION MÉTIER
    if not filepath.startswith(TARGET_PATH) and filename.startswith("MM_"):
        layout = self.layout
        layout.alert = True
        layout.operator("wm.checkpath_fake_menu", icon="ERROR")
        layout.alert = False

classes = (
    CHECKPATH_MT_menu,
    CHECKPATH_OT_fake_menu,
    CHECKPATH_OT_manual_check,
)
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_alert_menu)
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_alert_menu)