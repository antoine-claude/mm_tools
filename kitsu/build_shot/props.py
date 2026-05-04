"""
Build Shot specific properties (output folders, render settings).
Episode/Shot/Asset selection now comes from Kitsu props via context.scene.kitsu.
"""

import bpy
from .. import cache
from ..props import get_safely_string_prop, get_enum_item_names, set_kitsu_entity_id_via_enum_name
from . import core


def _get_asset_selected_via_name(self):
    """Get the selected asset name using shared helper."""
    return get_safely_string_prop(self, "asset_selected")


def _set_asset_selected_via_name(self, input_value):
    """Set the selected asset name, validating against active asset type and scope.
    
    Works like kitsu.asset_active_name but with scope override from build_shot.asset_scope.
    """
    asset_scope = self.asset_scope
    
    # Invalidate cache to get fresh assets list
    cache._asset_cache_asset_type_id = ""
    
    # Get enum items for current asset_type (from kitsu context) and scope
    enum_items = cache.get_assets_enum_for_active_asset_type(
        self, bpy.context, asset_scope=asset_scope
    )
    
    # Use standard setter with validation
    set_kitsu_entity_id_via_enum_name(
        self=self,
        input_name=input_value,
        items=enum_items,
        name_prop='asset_selected',
        id_prop='asset_selected_id',
    )


def _get_asset_search_list(self, context, edit_text):
    """Return list of available asset names for search, based on current asset_type and scope."""
    try:
        asset_scope = self.asset_scope
        enum_items = cache.get_assets_enum_for_active_asset_type(
            self, context, asset_scope=asset_scope
        )
        return get_enum_item_names(enum_items)
    except Exception:
        return []


def _on_asset_scope_update(self, context):
    """Invalidate cache and clear invalid asset selection when scope changes."""
    # Invalidate cache so next access recomputes with new scope
    cache._asset_cache_asset_type_id = ""
    
    # Clear selection if invalid for new scope
    current_value = self.get("asset_selected", "")
    if not current_value:
        return

    # Verify current selection is valid for new scope
    enum_items = cache.get_assets_enum_for_active_asset_type(
        self, context, asset_scope=self.asset_scope
    )
    enum_names = get_enum_item_names(enum_items)
    
    if current_value not in enum_names:
        self["asset_selected"] = ""



class BUILD_SHOT_property_group(bpy.types.PropertyGroup):
    """Property group for build shot output settings."""
    
    # Output path
    output_path: bpy.props.StringProperty(
        name="Output Path",
        description="Folder where to save the shot file",
        subtype='DIR_PATH',
        get= core.set_render_filepath,
        default=""
    )

    # Asset filter type - now delegated to kitsu.asset_type_active_name
    # (no longer a separate property in build_shot)

    # Asset scope - choose between project-wide or episode-specific assets
    asset_scope: bpy.props.EnumProperty(
        name="Asset Scope",
        description="Show assets from entire project or current episode",
        items=[
            ('PROJECT', "Project", "Show all assets from the active project"),
            ('EPISODE', "Episode", "Show only assets assigned to the current episode"),
        ],
        default='PROJECT',
        update=_on_asset_scope_update,
    )

    # Selected asset ID (linked to name property below)
    asset_selected_id: bpy.props.StringProperty(  # type: ignore
        name="Asset ID",
        description="ID of the selected asset",
        default="",
    )

    # Selected asset name - with search and filtering
    asset_selected: bpy.props.StringProperty(
        name="Asset",
        description="Currently selected asset (filtered by asset type from kitsu context and scope)",
        default="",  # type: ignore
        get=_get_asset_selected_via_name,
        set=_set_asset_selected_via_name,
        options=set(),
        search=_get_asset_search_list,
        search_options={'SORT'},
    )

    def get_assets(self):
        return self.get("_assets_expanded", True)

    def set_assets(self, value):
        self["_assets_expanded"] = value

    # Collapse/expand assets section
    assets_expanded: bpy.props.BoolProperty(
        name="Assets",
        description="Expand/collapse assets linking section",
        default= True,
        get=get_assets,
        set=set_assets
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
