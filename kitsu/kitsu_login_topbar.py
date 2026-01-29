import bpy
import gazu
import urllib.request
ADDON_NAME = "mm_tools"

# --------------------------------------------------
# STATE (module-level, partagé)
# --------------------------------------------------

_cached_projects = [("NONE", "-- Select a project --", "")]
_kitsu_reachable = False
_kitsu_user = None
_kitsu_checked = False


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_kitsu_host():
    """Dynamically get the kitsu_link from preferences."""

    prefs = bpy.context.preferences.addons[ADDON_NAME].preferences
        # print("Kitsu Link:", prefs.kitsu_link)
    if not prefs.kitsu_link.endswith("/api"):
        prefs.kitsu_link = prefs.kitsu_link+"/api"
    return prefs.kitsu_link



def is_logged():
    return _kitsu_user is not None


def load_projects():
    global _cached_projects
    if not is_logged():
        _cached_projects = [("NONE", "-- Select a project --", "")]
        return

    projects = gazu.project.all_projects()
    _cached_projects = [("NONE", "-- Select a project --", "")]
    for project in projects:
        _cached_projects.append(
            (project["id"], project["name"], project["name"])
        )


def get_projects_enum(self, context):
    return _cached_projects


def on_project_update(self, context):
    try:
        from .kitsu_playblast import load_tasks_for_project
        load_tasks_for_project(self.project_id)
    except Exception:
        pass

    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            area.tag_redraw()


def external_update_kitsu_host(self, context):
    """External update callback for Kitsu host changes from other prefs (e.g. DemoPreferences).
    Keeps the same behavior as KITSU_AddonPreferences.update_kitsu_host but callable from elsewhere.
    """
    global KITSU_HOST, _kitsu_reachable, _kitsu_user
    KITSU_HOST = get_kitsu_host()
    try:
        gazu.set_host(KITSU_HOST)
    except Exception:
        pass
    _kitsu_reachable = False
    _kitsu_user = None
    load_projects()


# KITSU preferences moved to the addon's central preferences (DemoPreferences in updater_ui.py).
# The original KITSU_AddonPreferences class was removed to avoid duplicate registrations
# and keep preferences centralized.
# (Any callbacks still reference helpers in this module, e.g. external_update_kitsu_host.)


# --------------------------------------------------
# OPERATORS
# --------------------------------------------------

class KITSU_OT_Login(bpy.types.Operator):
    bl_idname = "kitsu.login"
    bl_label = "Login to Kitsu"

    username: bpy.props.StringProperty(name="User")
    password: bpy.props.StringProperty(name="Password", subtype='PASSWORD')
    remember: bpy.props.BoolProperty(name="Remember credentials", default=True)

    def execute(self, context):
        prefs = context.preferences.addons[ADDON_NAME].preferences
        try:
            KITSU_HOST = get_kitsu_host()
            gazu.set_host(KITSU_HOST)

            gazu.log_in(self.username, self.password)
            user = gazu.client.get_current_user()
            # Update cached state
            global _kitsu_reachable, _kitsu_user
            _kitsu_reachable = True
            _kitsu_user = user
            if self.remember:
                prefs.remember_credentials = True
                prefs.saved_username = self.username
                prefs.saved_password = self.password
            else:
                prefs.remember_credentials = False
                prefs.saved_username = ""
                prefs.saved_password = ""
            load_projects()  # Recharge les projets après le login
            # Ensure tasks are reloaded if the file is open
            try:
                from .kitsu_playblast import load_tasks_for_project
                load_tasks_for_project(prefs.project_id)
            except Exception:
                pass
            self.report({'INFO'}, f"Logged in as {user['full_name']}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Mail ou mot de passe incorrect: {str(e)}")
            prefs.saved_password = ""
            self.password = prefs.saved_password
            return {'CANCELLED'}
        
    def invoke(self, context, event):
        prefs = context.preferences.addons[ADDON_NAME].preferences
        if prefs.saved_username and prefs.saved_password and prefs.remember_credentials:
            self.username = prefs.saved_username
            self.password = prefs.saved_password
            self.remember = prefs.remember_credentials
            return self.execute(context)
        else:
            if prefs.saved_username:
                self.username = prefs.saved_username
            # Ne pas pré-remplir le mot de passe si on affiche la boîte de dialogue
            self.password = ""
            self.remember = prefs.remember_credentials
            return context.window_manager.invoke_props_dialog(self)


class KITSU_OT_Logout(bpy.types.Operator):
    bl_idname = "kitsu.logout"
    bl_label = "Logout from Kitsu"

    def execute(self, context):
        try:
            gazu.log_out()
        except Exception:
            pass

        # Update cached state
        global _kitsu_reachable, _kitsu_user
        _kitsu_user = None
        _kitsu_reachable = True

        prefs = context.preferences.addons[ADDON_NAME].preferences
        prefs.project_id = "NONE"
        prefs.saved_username = ""
        prefs.saved_password = ""
        prefs.remember_credentials = False
        load_projects()  # Réinitialise les projets après le logout
        try:
            from .kitsu_playblast import load_tasks_for_project
            load_tasks_for_project("NONE")
        except Exception:
            pass

        self.report({'INFO'}, "Logged out from Kitsu")
        return {'FINISHED'}


# --------------------------------------------------
# UI
# --------------------------------------------------

def draw_kitsu_topbar(self, context):
    layout = self.layout
    layout.separator()

    prefs = context.preferences.addons[ADDON_NAME].preferences
    if not _kitsu_reachable:
        layout.label(text="Kitsu: unreachable", icon='ERROR')
        layout.operator("kitsu.reconnect", text="", icon='PLUGIN')
    else:
        if _kitsu_user:
            layout.label(text=f"Kitsu: {prefs.saved_username or _kitsu_user.get('full_name','')}", icon='CHECKMARK')
            layout.operator("kitsu.logout", text="", icon='X')
        else:
            layout.operator("kitsu.login", text="Log to Kitsu", icon='USER')


# --------------------------------------------------
# HANDLERS
# --------------------------------------------------

def initial_kitsu_check():
    global _kitsu_reachable, _kitsu_user, _kitsu_checked
    _kitsu_checked = True

    try:
        gazu.set_host(get_kitsu_host())
        urllib.request.urlopen(get_kitsu_host(), timeout=1)
        _kitsu_reachable = True
        try:
            _kitsu_user = gazu.client.get_current_user()
        except Exception:
            _kitsu_user = None
        load_projects()
    except Exception:
        _kitsu_reachable = False

    return None


def check_kitsu_once(timeout=1.0):
    """Check if the Kitsu host is reachable within timeout seconds.
    Updates global _kitsu_reachable and _kitsu_user and loads projects if reachable.
    This must NOT be called from a draw function.
    """
    global _kitsu_reachable, _kitsu_user, _kitsu_checked
    _kitsu_checked = True
    try:
        with urllib.request.urlopen(KITSU_HOST, timeout=timeout) as response:
            # If we get a response without exception, consider host reachable
            _kitsu_reachable = True
        # Try to fetch current user (may fail if not logged)
        try:
            _kitsu_user = gazu.client.get_current_user()
        except Exception:
            _kitsu_user = None
        # Load projects if host reachable
        load_projects()
    except Exception:
        _kitsu_reachable = False
        _kitsu_user = None

class KITSU_OT_Reconnect(bpy.types.Operator):
    bl_idname = "kitsu.reconnect"
    bl_label = "Reconnect to Kitsu"

    def execute(self, context):
        check_kitsu_once(timeout=1.0)
        if _kitsu_reachable:
            self.report({'INFO'}, "Reconnected to Kitsu")
        else:
            self.report({'ERROR'}, "Unable to reach Kitsu")
        return {'FINISHED'}

class KITSU_OT_UnreachablePopup(bpy.types.Operator):
    bl_idname = "kitsu.unreachable_popup"
    bl_label = "Kitsu unreachable"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Unable to reach the Kitsu server (timeout 1s).")
        layout.label(text="You can try to reconnect from the topbar.")

    def execute(self, context):
        return {'FINISHED'}

class KITSU_PT_ContextPanel(bpy.types.Panel):
    bl_label = "Kitsu Context"
    bl_idname = "KITSU_PT_context"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Kitsu'

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[ADDON_NAME].preferences

        if not _kitsu_reachable:
            layout.label(text="Kitsu server unreachable", icon='ERROR')
            return

        if not is_logged():
            layout.label(text="Please log to Kitsu")
            return

        layout.label(text="Active Project:")
        layout.prop(prefs, "project_id", text="")

# --------------------------------------------------
# EXPORTS (IMPORTANT)
# --------------------------------------------------

classes = (
    KITSU_OT_Login,
    KITSU_OT_Logout,
    KITSU_OT_Reconnect,
    KITSU_OT_UnreachablePopup,
    KITSU_PT_ContextPanel,
)

def get_classes():
    return classes

def get_draw_funcs():
    return [draw_kitsu_topbar]
