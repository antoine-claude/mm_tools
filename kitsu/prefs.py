"""
Addon preferences for mm_tools Kitsu integration.
Handles authentication, project settings, and credential storage.
"""

from pathlib import Path
import hashlib
import sys
import os

import bpy
from .types import Session
from .auth.ops import (
    KITSU_OT_con_productions_load,
    KITSU_OT_session_end,
    KITSU_OT_session_start,
)
from . import cache

def session_get(context: bpy.types.Context) -> Session:
    """
    Shortcut to get session from blender_kitsu addon preferences
    """
    root = __package__.split(".")[0]
    prefs = context.preferences.addons[root].preferences
    return prefs.session  # type: ignore


def addon_prefs_get(context: bpy.types.Context) -> bpy.types.AddonPreferences:
    """
    Shortcut to get blender_kitsu addon preferences
    """
    root = __package__.split(".")[0]
    return context.preferences.addons[root].preferences


def project_root_dir_get(context: bpy.types.Context):
    addon_prefs = addon_prefs_get(context)
    return Path(addon_prefs.project_root_dir)
    # return Path(addon_prefs.project_root_dir).joinpath('svn').resolve()

def asset_dir_get(context: bpy.types.Context):
    addon_prefs = addon_prefs_get(context)
    return Path(addon_prefs.asset_dir)

def session_auth(context: bpy.types.Context) -> bool:
    """
    Shortcut to check if zession is authorized
    """
    return session_get(context).is_auth()



class KITSU_task(bpy.types.PropertyGroup):
    # name: StringProperty() -> Instantiated by default
    id: bpy.props.StringProperty(name="Task ID", default="")
    entity_id: bpy.props.StringProperty(name="Entity ID", default="")
    entity_name: bpy.props.StringProperty(name="Entity Name", default="")
    task_type_id: bpy.props.StringProperty(name="Task Type ID", default="")
    task_type_name: bpy.props.StringProperty(name="Task Type Name", default="")

class MMToolsPreferences(bpy.types.AddonPreferences):
    """
    Addon preferences for mm_tools with Kitsu integration.
    Handles authentication, project selection, and credential storage.
    """
    
    bl_idname = __package__.split(".")[0]

    # --------- KITSU AUTHENTICATION ---------
    
    host: bpy.props.StringProperty(
        name="Kitsu Host",
        description="URL to Kitsu server (e.g., https://kitsu.example.com)",
        default="",
    )
    
    email: bpy.props.StringProperty(
        name="Email",
        description="Email address for Kitsu authentication",
        default="",
    )
    
    passwd: bpy.props.StringProperty(
        name="Password",
        description="Password for Kitsu authentication",
        default="",
        subtype="PASSWORD",
        options={"HIDDEN", "SKIP_SAVE"},
    )
    
    # --------- UPDATER PROPERTIES ---------
    
    auto_check_update: bpy.props.BoolProperty(
        name="Auto Check Update",
        description="Automatically check for addon updates",
        default=True,
    )
    
    updater_interval_months: bpy.props.IntProperty(
        name="Updater Interval Months",
        description="Months interval for checking updates",
        default=0,
    )
    
    updater_interval_days: bpy.props.IntProperty(
        name="Updater Interval Days",
        description="Days interval for checking updates",
        default=7,
    )
    
    updater_interval_hours: bpy.props.IntProperty(
        name="Updater Interval Hours",
        description="Hours interval for checking updates",
        default=0,
    )
    
    updater_interval_minutes: bpy.props.IntProperty(
        name="Updater Interval Minutes",
        description="Minutes interval for checking updates",
        default=0,
    )
    
    # --------- PROJECT SELECTION ---------
    
    project_id: bpy.props.StringProperty(
        name="Project ID",
        description="Active Kitsu project ID",
        default="NONE",
    )
    
    project_root_dir: bpy.props.StringProperty(
        name="Project Root Directory",
        description="Root directory path for the active project",
        default="",
        subtype="DIR_PATH",
    )
    
    project_active_id: bpy.props.StringProperty(  # type: ignore
        name="Project Active ID",
        description="Server Id that refers to the last active project",
        default="",
    )

    asset_dir: bpy.props.StringProperty(
        name="Assets Root Directory",
        description="Asset directory path from the active project",
        default="",
        subtype="DIR_PATH",
    )

    pb_open_webbrowser: bpy.props.BoolProperty(  # type: ignore
        name="Open Webbrowser after Playblast",
        description="Toggle if the default webbrowser should be opened to kitsu after playblast creation",
        default=False,
    )

    pb_open_vse: bpy.props.BoolProperty(  # type: ignore
        name="Open Sequence Editor after Playblast",
        description="Toggle if the movie clip should be loaded in the seqeuence editor in a seperate scene after playblast creation",
        default=False,
    )

    pb_manual_burn_in: bpy.props.BoolProperty(  # type: ignore
        name="Manual Playblast Burn-Ins",
        description=(
            "Blender Kitsu will override all Shot/Sequence playblasts with it's own metadata burn in. "
            "This includes frame, lens, Shot name & Animator name at font size of 24. "
            "To use a file's metadata burn in settings during playblast enable this option"
        ),
        default=False,
    )

    session: Session = Session()


    tasks: bpy.props.CollectionProperty(type=KITSU_task)
    # Session instance stored on preferences
    session: Session = Session()

    def draw(self, context):
        """Draw addon preferences UI."""
        from .. import addon_updater_ops
        
        layout = self.layout
        
        # ========== KITSU SECTION ==========
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        flow = layout.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=True, align=False
        )
        col = flow.column()
        project_active = cache.project_active_get()
        # Authentication status and controls
        box = col.box()
        box.label(text="Login and Host Settings", icon="URL")
        if not self.session.is_auth():
            box.row().prop(self, "host")
            box.row().prop(self, "email")
            box.row().prop(self, "passwd")
            box.row().operator(KITSU_OT_session_start.bl_idname, text="Login", icon="PLAY")
        else:
            row = box.row()
            row.prop(self, "host")
            row.enabled = False
            box.row().label(text=f"Logged in: {self.session.email}")
            box.row().operator(KITSU_OT_session_end.bl_idname, text="Logout", icon="PANEL_CLOSE")
    
       # Project
        box = col.box()
        box.label(text="Project", icon="FILEBROWSER")
        row = box.row(align=True)

        if not project_active:
            prod_load_text = "Select Project"
        else:
            prod_load_text = project_active.name

        row.operator(
            KITSU_OT_con_productions_load.bl_idname,
            text=prod_load_text,
            icon="DOWNARROW_HLT",
        )
        box.row().prop(self, "project_root_dir")
        
        # ========== ASSET SECTION ==========
        box = col.box()
        box.label(text="Asset", icon="ASSET_MANAGER")
        box.row().prop(self, "asset_dir")

        # Previews
        box = col.box()
        box.label(text="Previews", icon="RENDER_ANIMATION")
        # box.row().prop(self, "shot_playblast_root_dir")
        # box.row().prop(self, "seq_playblast_root_dir")
        # box.row().prop(self, "frames_root_dir")

        # box.row().prop(self, "pb_open_webbrowser")
        # box.row().prop(self, "pb_open_vse")
        # box.row().prop(self, "pb_manual_burn_in")

        # ========== UPDATER SECTION ==========
        mainrow = layout.row()
        col = mainrow.column()
        addon_updater_ops.update_settings_ui(self, context)


classes = [
    KITSU_task,
    MMToolsPreferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    # Log user out.
    root = __package__.split(".")[0]
    addon_prefs = bpy.context.preferences.addons[root].preferences
    if addon_prefs.session.is_auth():
        addon_prefs.session.end()

    # Unregister classes.
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
