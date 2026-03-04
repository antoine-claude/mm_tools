"""
Build Shot specific properties (output folders, render settings).
Episode/Shot/Asset selection now comes from Kitsu props via context.scene.kitsu.
"""

import bpy
from .. import cache


def _get_asset_selected_via_name(self):
    """Get the selected asset name"""
    try:
        return self.get("asset_selected", "")
    except:
        return ""


def _set_asset_selected_via_name(self, value):
    """Set the selected asset name"""
    if value == "":
        self["asset_selected"] = ""
        return
    
    # Verify the asset exists in filtered list using cached function
    try:
        asset_filter = bpy.context.scene.build_shot.asset_filter
        asset_scope = bpy.context.scene.build_shot.asset_scope
        filtered_assets = cache.get_filtered_assets_for_buildshot(bpy.context, asset_filter, asset_scope)
        asset_names = [a.name for a in filtered_assets]
        
        if value in asset_names:
            self["asset_selected"] = value
    except:
        pass


def _get_asset_search_list(self, context, edit_text):
    """Return list of available filtered asset names for search using cached function"""
    try:
        asset_filter = context.scene.build_shot.asset_filter
        asset_scope = context.scene.build_shot.asset_scope
        filtered_assets = cache.get_filtered_assets_for_buildshot(context, asset_filter, asset_scope)
        return [a.name for a in filtered_assets]
    except:
        return []


class BUILD_SHOT_property_group(bpy.types.PropertyGroup):
    """Property group for build shot output settings."""
    
    # Output folder selection: Lighting, Animation, Layout
    type_folder: bpy.props.EnumProperty(
        name="Task Output Folder",
        description="Choose the output folder/layer for linked assets",
        items=[
            ('Layout', "Layout", "Layout folder output"),
            ('Animation', "Animation", "Animation folder output"),
            ('Lighting', "Lighting", "Lighting folder output"),
        ],
        default='Layout'
    )

    # Animation sub-folder selection
    anim_sub_folder: bpy.props.EnumProperty(
        name="Animation Sub Folder",
        description="Choose the animation subfolder for linked assets",
        items=[
            ('Animation_Blocking', "Animation Blocking", "Animation Blocking folder output"),
            ('Animation_Spline', "Animation Spline", "Animation Spline folder output"),
            ('Animation_Stopmo', "Animation Stopmo", "Animation Stopmo folder output"),
        ],
        default='Animation_Blocking'
    )

    # Output path
    output_path: bpy.props.StringProperty(
        name="Output Path",
        description="Folder where to save the shot file",
        subtype='DIR_PATH',
        default=""
    )
    
    # Link override option
    link_override: bpy.props.BoolProperty(
        name="Link Override",
        description="Create link override instead of regular link",
        default=True
    )

    # Asset filter type
    asset_filter: bpy.props.EnumProperty(
        name="Asset Filter",
        description="Filter assets by type",
        items=[
            ('ALL', "All", "Show all assets"),
            ('CHR', "Characters", "Show only character assets"),
            ('PRP', "Props", "Show only prop assets"),
            ('SET', "Sets", "Show only set assets"),
            ('ITM', "Items", "Show only set item assets"),
        ],
        default='ALL'
    )

    # Asset scope - choose between project-wide or shot-specific assets
    asset_scope: bpy.props.EnumProperty(
        name="Asset Scope",
        description="Show assets from entire project or only from current shot",
        items=[
            ('PROJECT', "Project", "Show all assets from the active project"),
            ('SHOT', "Shot", "Show only assets assigned to the current shot"),
        ],
        default='PROJECT'
    )

    # Selected asset name - with search and filtering
    asset_selected: bpy.props.StringProperty(
        name="Asset",
        description="Currently selected asset from the project (filtered by Asset Filter)",
        default="",  # type: ignore
        get=_get_asset_selected_via_name,
        set=_set_asset_selected_via_name,
        options=set(),
        search=_get_asset_search_list,
        search_options={'SORT'},
    )

    # Collapse/expand assets section
    assets_expanded: bpy.props.BoolProperty(
        name="Assets",
        description="Expand/collapse assets linking section",
        default=True
    )

    link_options_expanded: bpy.props.BoolProperty(
        name="Linking Options",
        description="Expand/collapse operator linking section",
        default=True
    )
classes = (BUILD_SHOT_property_group,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.build_shot = bpy.props.PointerProperty(type=BUILD_SHOT_property_group)


def unregister():
    if hasattr(bpy.types.Scene, "build_shot"):
        del bpy.types.Scene.build_shot
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
