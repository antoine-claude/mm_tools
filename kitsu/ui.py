"""
UI helper functions for Kitsu integration.
"""

import bpy


def draw_error_box(layout: bpy.types.UILayout) -> bpy.types.UILayout:
    """Draw an error box."""
    box = layout.box()
    box.label(text="Error", icon="ERROR")
    return box


def draw_error_active_project_unset(box: bpy.types.UILayout) -> None:
    """Draw error for no active project."""
    row = box.row(align=True)
    row.label(text="No Active Project")
    row.operator(
        "preferences.addon_show", text="Open Addon Preferences"
    ).module = __package__


def draw_error_kitsu_unreachable(box: bpy.types.UILayout) -> None:
    """Draw error for Kitsu server unreachable."""
    row = box.row(align=True)
    row.label(text="Kitsu Server Unreachable")
    row.operator(
        "preferences.addon_show", text="Open Addon Preferences"
    ).module = __package__


def draw_error_not_authenticated(box: bpy.types.UILayout) -> None:
    """Draw error for not authenticated."""
    row = box.row(align=True)
    row.label(text="Not Authenticated")
    row.operator(
        "preferences.addon_show", text="Open Addon Preferences"
    ).module = __package__

def draw_error_no_active_camera(
    box: bpy.types.UILayout,
) -> bpy.types.UILayout:
    row = box.row(align=True)
    row.label(text=f"No active camera")
    row.prop(bpy.context.scene, "camera", text="")
