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
from .core import set_shot_filepath, draw_assets_for_shot, get_highest_version_file, draw_linking_options
from ..context import core as context_core
from .. import cache, prefs, ui




def _get_new_output_path(context: bpy.types.Context) -> str | None:
    """Compute and return the output path for the current shot"""
    return set_shot_filepath(
        prefs.project_root_dir_get(context),
        context.scene.kitsu.episode_active_name,
        context.scene.kitsu.sequence_active_name,
        context.scene.kitsu.shot_active_name,
        context.scene.build_shot.type_folder,
        context.scene.build_shot.anim_sub_folder
    )

def draw_output_type_layer_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw output layer selection (type_folder and animation subfolder)"""
    layout.label(text="Output Task Folder :")
    row = layout.row(align=True)
    row.prop(context.scene.build_shot, "type_folder")

def draw_output_animation_subfolder_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw animation subfolder selector, only if type_folder is set to Animation"""
    if context.scene.build_shot.type_folder == "Animation":
        row = layout.row(align=True)
        row.prop(context.scene.build_shot, "anim_sub_folder")

def draw_asset_filter_and_selector(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw asset scope selector, filter and asset selection in split row"""
    # Asset scope selector
    layout.label(text="Add Asset out of casting : ")
    box = layout.box()
    box.prop(context.scene.build_shot, "asset_scope", text="Asset Scope")
    
    row = box.row(align=True)
    row.use_property_split = False
    
    # Filter column (0.2 width)
    split = row.split(factor=0.2, align=True)
    split.prop(context.scene.build_shot, "asset_filter", text="")
    
    # Asset selection column (0.8 width)
    col = split.column(align=True)
    col.prop(context.scene.build_shot, "asset_selected", text="")
    
    # Add button to add selected asset to buildshot selection
    row_add = box.row(align=True)
    row_add.operator(
        "build_shot.add_asset_to_selection",
        text="Add to Selection",
        icon='ADD'
    )
    row.separator()

def draw_build_shot_section(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw build shot output path and build button"""
    shot_active = cache.shot_active_get()
    if not shot_active or not shot_active.id:
        return
    
    output_path = _get_new_output_path(context)
    highest_version = get_highest_version_file(output_path)

    if not highest_version:
        if not os.path.exists(os.path.dirname(output_path)):
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            print(f"Folder {os.path.dirname(output_path)} does not exist")
            row.label(text=f"Folder {context.scene.build_shot.type_folder} missing",
                       icon="ERROR")
            return
        layout.label(text=f"Output Path: {output_path}")
        # Build shot button - conditional based on type_folder
        if context.scene.build_shot.type_folder == "Animation":
            layout.operator(
                "build_shot.build_shot_animation",
                text="Build Animation Shot",
                icon='FILE_TICK'
            )
        else:
            layout.operator(
                "build_shot.build_shot_layout",
                text="Build Layout Shot",
                icon='FILE_TICK'
            )
    elif highest_version and os.path.exists(highest_version):
        if bpy.data.filepath == highest_version:
            layout.label(text=f"Actual File",icon="CHECKMARK")
        else :
            #Open existing file button
            layout.label(text=f"Shot already built: {highest_version}",
                        icon="CHECKMARK")
            open_file = layout.operator(
                "wm.open_mainfile",
                text="Open Existing Shot",
                icon='FILE_FOLDER'
            )
            open_file.filepath = highest_version
            open_file.load_ui = False
            open_file.display_file_selector = False


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
        row.operator("build_shot.get_current_context", text="", icon="FILE_REFRESH" )
        
        
        flow = layout.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=False
        )
        col = flow.column()
        # col.prop(context.scene.kitsu, "category")
        # Episode selector
        context_core.draw_episode_selector(context, col)
        # Sequence selector
        context_core.draw_sequence_selector(context, col)
        
        # Shot selector
        context_core.draw_shot_selector(context, col)

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
        

        layout.use_property_split = True
        flow = layout.grid_flow(
        row_major=True, columns=0, even_columns=True, even_rows=False, align=False
        )
        col = flow.column()
        # Output layer selection
        draw_output_type_layer_selector(context, col)
        draw_output_animation_subfolder_selector(context, col)

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
