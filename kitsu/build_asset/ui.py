"""
UI for build_shot addon
Provides panels for shot building workflow using Kitsu integration
"""

from calendar import c
from re import S

import bpy
import os
from bpy.types import Panel
from pathlib import Path
from ..build_shot.core import draw_assets_for_shot, draw_linking_options, draw_asset_filter_and_selector, draw_build_shot_section
from ..context import core as context_core
from .. import cache, prefs, ui, bkglobals

class BUILD_ASSET_PT_main_panel(Panel):
    """Main panel for Shot Builder addon"""
    bl_label = "Asset Builder"
    bl_idname = "BUILD_ASSET_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Kitsu"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 40

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Show panel if Kitsu is authenticated"""
        return prefs.session_auth(context) and context_core.is_asset_context()
    
    @classmethod
    def poll_error(cls, context: bpy.types.Context) -> bool:
        project_active = cache.project_active_get()
        return bool(not project_active)
    
    def draw(self, context: bpy.types.Context) -> None:
        scene = context.scene
        kitsu_scene = scene.kitsu
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        project_active = cache.project_active_get()
        task_type = cache.task_type_active_get()

        # Catch errors
        if self.poll_error(context):
            box = ui.draw_error_box(layout)
            if not project_active:
                ui.draw_error_active_project_unset(box)
            return

        # Production header
        row = layout.row()
        # row.label(text=f"Production: {project_active.name}")
        # row.operator("kitsu.get_current_context", text="", icon="FILE_REFRESH" )
        
        
        flow = layout.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=False
        )
        col = flow.column()


        if not prefs.session_auth(context) or not project_active:
            row.enabled = False
        # AssetType selector (if context is Asset)
        # if context_core.is_asset_context():
        #     context_core.draw_asset_type_selector(context, col)
        #     context_core.draw_asset_selector(context, col)
        #     context_core.draw_task_type_selector(context, col)

        row = col.row()
        row.operator("kitsu.build_asset_modeling", text=f"Build Asset {task_type.name}")

classes = (
    BUILD_ASSET_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
