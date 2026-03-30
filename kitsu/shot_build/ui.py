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
from .core import draw_assets_for_shot, draw_linking_options, draw_asset_filter_and_selector, draw_build_shot_section
from ..context import core as context_core
from .. import cache, prefs, ui

class BUILD_SHOT_PT_main_panel(Panel):
    """Main panel for Shot Builder addon"""
    bl_label = "Shot Builder"
    bl_idname = "BUILD_SHOT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Kitsu"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Show panel if Kitsu is authenticated"""
        return prefs.session_auth(context)

    @classmethod
    def poll_error(cls, context: bpy.types.Context) -> bool:
        project_active = cache.project_active_get()
        return bool(not project_active)
    
    def draw(self, context: bpy.types.Context) -> None:
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        project_active = cache.project_active_get()

        # Catch errors
        if self.poll_error(context):
            box = ui.draw_error_box(layout)
            if not project_active:
                ui.draw_error_active_project_unset(box)
            return

        # Production header
        row = layout.row()
        row.label(text=f"Production: {project_active.name}")
        row.operator("kitsu.get_current_context", text="", icon="FILE_REFRESH" )
        
        
        flow = layout.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=False
        )
        col = flow.column()
        # Entity context
        # col.prop(context.scene.kitsu, "category")

        if not prefs.session_auth(context) or not project_active:
            row.enabled = False

        # col.prop(context.scene.kitsu, "category")
        # Episode selector
        context_core.draw_episode_selector(context, col)
        if context_core.is_shot_context():
            # Sequence selector
            context_core.draw_sequence_selector(context, col)
            # Shot selector
            context_core.draw_shot_selector(context, col)
            col.separator()
            #Department selector
            context_core.draw_department_selector(context, col)
            #Task type selector selector
            context_core.is_task_type_list_for_department(context)

            if context_core.is_department_context(context) :
                if context_core.is_task_type_list_for_department(context) :
                    context_core.draw_task_type_department_selector(context, col)
        # Asset selection for the shot
        col.separator()

        # Display expandable assets section with bool property
        assets_row = col.row()
        assets_row.prop(scene.build_shot, "assets_expanded", text="", emboss=False, icon='TRIA_DOWN' if scene.build_shot.assets_expanded else 'TRIA_RIGHT')
        assets_row.label(text="Assets Selection :")
        # Only show assets content if expanded
        layout.use_property_split = False
        if scene.build_shot.assets_expanded:
            draw_assets_for_shot(context, col)
            box = col.box()
            draw_asset_filter_and_selector(context, box)
            # Asset filter and selector with split layout
            draw_linking_options(context, box)
        

        # layout.use_property_split = True
        # flow = layout.grid_flow(
        # row_major=True, columns=0, even_columns=True, even_rows=False, align=False
        # )
        # col = flow.column()
        # # Output layer selection
                

        # Build shot section
        draw_build_shot_section(context, layout)

classes = (
    BUILD_SHOT_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
