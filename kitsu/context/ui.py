from calendar import c
from re import S

import bpy
import os
from bpy.types import Panel
from pathlib import Path
from ..context import core as context_core
from .. import cache, prefs, ui, bkglobals


class KITSU_PT_vi3d_context(bpy.types.Panel):
    """
    Panel in 3dview that enables browsing through backend data structure.
    Thought of as a menu to setup a context by selecting active production
    active sequence, shot etc.
    """

    bl_category = "Kitsu"
    bl_label = "Context"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 20

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

        if not prefs.session_auth(context) or not project_active:
            row.enabled = False
        # Entity context
        # col.prop(context.scene.kitsu, "category")
        # Episode selector
        if project_active.production_type == bkglobals.KITSU_TV_PROJECT:
            if context_core.is_shot_context():
                context_core.draw_episode_selector(context, col)
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

            if context_core.is_asset_context():
                context_core.draw_asset_type_selector(context, col)
                context_core.draw_asset_selector(context, col)
                context_core.draw_task_type_selector(context, col)

    
classes = (
    KITSU_PT_vi3d_context,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
