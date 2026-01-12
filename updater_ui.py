from multiprocessing import context
import bpy

# Updater ops import, all setup in this file.
from . import addon_updater_ops

# Try to reuse Kitsu helpers (fall back to safe defaults if missing)
try:
    from .kitsu.kitsu_login_topbar import get_projects_enum, on_project_update, external_update_kitsu_host, _cached_projects
except Exception:
    get_projects_enum = lambda self, context: [("NONE", "-- Select a project --", "")]
    on_project_update = lambda self, context: None
    external_update_kitsu_host = lambda self, context: None
    _cached_projects = [("NONE", "-- Select a project --", "")]



class DemoUpdaterPanel(bpy.types.Panel):
    """Panel to demo popup notice and ignoring functionality"""
    bl_label = "Updater Demo Panel"
    bl_idname = "OBJECT_PT_DemoUpdaterPanel_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
    bl_context = "objectmode"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout

        # Call to check for update in background.
        # Note: built-in checks ensure it runs at most once, and will run in
        # the background thread, not blocking or hanging blender.
        # Internally also checks to see if auto-check enabled and if the time
        # interval has passed.
        addon_updater_ops.check_for_update_background()

        layout.label(text="Demo Updater Addon")
        layout.label(text="")

        col = layout.column()
        col.scale_y = 0.7
        col.label(text="If an update is ready,")
        col.label(text="popup triggered by opening")
        col.label(text="this panel, plus a box ui")

        # Could also use your own custom drawing based on shared variables.
        if addon_updater_ops.updater.update_ready:
            layout.label(text="Custom update message", icon="INFO")
        layout.label(text="")

        # Call built-in function with draw code/checks.
        addon_updater_ops.update_notice_box_ui(self, context)


@addon_updater_ops.make_annotations
class DemoPreferences(bpy.types.AddonPreferences):
    """Demo bare-bones preferences"""
    bl_idname = __package__

    # Addon updater preferences.

    auto_check_update = bpy.props.BoolProperty(name="Auto-check for Update",description="If enabled, auto-check for updates using an interval",default=False)
    updater_interval_months = bpy.props.IntProperty(name='Months',description="Number of months between checking for updates",default=0,min=0)
    updater_interval_days = bpy.props.IntProperty(name='Days',description="Number of days between checking for updates",default=7,min=0,max=31)
    updater_interval_hours = bpy.props.IntProperty(name='Hours',description="Number of hours between checking for updates",default=0,min=0,max=23)
    updater_interval_minutes = bpy.props.IntProperty(name='Minutes',description="Number of minutes between checking for updates",default=0,min=0,max=59)

    # Kitsu preferences (centralized here for the addon)
    kitsu_link = bpy.props.StringProperty(
        name="Kitsu Link",
        description="Lien vers le serveur Kitsu",
        default="https://kitsu.20stm-prod.be/api",
        update=external_update_kitsu_host
    )

    project_id = bpy.props.EnumProperty(
        name="Project",
        items=get_projects_enum,
        update=on_project_update
    )

    saved_username = bpy.props.StringProperty(default="")
    saved_password = bpy.props.StringProperty(subtype="PASSWORD", default="")
    remember_credentials = bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout

        # Quick Kitsu status (prepended)
        try:
            from .kitsu.kitsu_login_topbar import _kitsu_reachable, _kitsu_user, _cached_projects
        except Exception:
            _kitsu_reachable = False
            _kitsu_user = None
            _cached_projects = [("NONE", "-- Select a project --", "")]

        # Find Kitsu prefs robustly (check known names then scan)
        kprefs = None
        for name in ( __package__, "mm_tools", "mm_tools.kitsu"):
            try:
                kprefs = context.preferences.addons[name].preferences
                break
            except Exception:
                kprefs = None

        if kprefs is None:
            for name in context.preferences.addons.keys():
                try:
                    p = context.preferences.addons[name].preferences
                    if hasattr(p, "kitsu_link"):
                        kprefs = p
                        break
                except Exception:
                    continue

        if kprefs:
            layout.prop(kprefs, "kitsu_link")
            if not _kitsu_reachable:
                layout.label(text="Kitsu server unreachable", icon='ERROR')
                layout.operator("kitsu.reconnect", text="Reconnect")
            else:
                if _kitsu_user:
                    # Show active project from cached projects
                    project_name = None
                    for pid, name, _ in _cached_projects:
                        if pid == kprefs.project_id:
                            project_name = name
                            break
                    if project_name and kprefs.project_id != "NONE":
                        layout.label(text=f"Active project: {project_name}")
                    else:
                        layout.label(text="No project selected")
                    layout.separator()
                    layout.label(text=f"Logged as: {_kitsu_user.get('full_name','')}")
                    row = layout.row()
                    row.prop(kprefs, "remember_credentials")
                    if kprefs.remember_credentials and kprefs.saved_username:
                        layout.label(text=f"Saved user: {kprefs.saved_username}")
                else:
                    layout.label(text="Not logged to Kitsu")
                    layout.separator()
                    layout.label(text="Saved credentials:")
                    row = layout.row()
                    row.prop(kprefs, "remember_credentials")
                    if kprefs.remember_credentials and kprefs.saved_username:
                        row = layout.row()
                        row.label(text=f"Saved user: {kprefs.saved_username}")
        else:
            layout.label(text="Not logged to Kitsu")
            layout.separator()
            layout.label(text="Saved credentials:")
            row = layout.row()
            row.prop(self, "remember_credentials")
            if self.remember_credentials and self.saved_username:
                row = layout.row()
                row.label(text=f"Saved user: {self.saved_username}")

        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        col = mainrow.column()

        # __package__.split('.')[:-1]

        # Updater draw function, could also pass in col as third arg.
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # ops = col.operator("wm.url_open","Open webpage ")
        # ops.url=addon_updater_ops.updater.website
        
classes=[DemoUpdaterPanel,DemoPreferences]