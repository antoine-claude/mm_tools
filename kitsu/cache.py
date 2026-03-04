# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
#
# (c) 2021, Blender Foundation - Paul Golter

from typing import Any, List, Union, Dict, Tuple

import bpy

from bpy.app.handlers import persistent

from .types import (
    Project,
    Episode,
    Edit,
    Sequence,
    Shot,
    Asset,
    AssetType,
    TaskType,
    Task,
    ProjectList,
    TaskStatus,
    Cache,
    User,
)
from .logger import LoggerFactory
import gazu

logger = LoggerFactory.getLogger()

# CACHE VARIABLES
# used to cache active entities to prevent a new api request when read only
_project_active: Project = Project()
_episode_active: Episode = Episode()
_sequence_active: Sequence = Sequence()
_shot_active: Shot = Shot()
_asset_active: Asset = Asset()
_edit_active: Edit = Edit()
_asset_type_active: AssetType = AssetType()
_task_type_active: TaskType = TaskType()
_user_active: User = User()
_user_all_tasks: List[Task] = []

_cache_initialized: bool = False
_cache_startup_initialized: bool = False

_episodes_enum_list: List[Tuple[str, str, str]] = []
_sequence_enum_list: List[Tuple[str, str, str]] = []
_shot_enum_list: List[Tuple[str, str, str]] = []
_asset_types_enum_list: List[Tuple[str, str, str]] = []
_asset_enum_list: List[Tuple[str, str, str]] = []
_projects_enum_list: List[Tuple[str, str, str]] = []
_task_types_enum_list: List[Tuple[str, str, str]] = []
_task_types_shots_enum_list: List[Tuple[str, str, str]] = []
_task_statuses_enum_list: List[Tuple[str, str, str]] = []
_user_all_tasks_enum_list: List[Tuple[str, str, str]] = []
_all_edits_enum_list: List[Tuple[str, str, str]] = []

_asset_cache_proj_id: str = ""
_episode_cache_proj_id: str = ""
_all_shot_tasks_cache_proj_id: str = ""
_all_task_type_cache_proj_id: str = ""
_seq_cache_proj_id: str = ""
_seq_cache_episode_id: str = ""
_shot_cache_seq_id: str = ""
_task_type_cache_shot_id: str = ""
_asset_cache_asset_type_id: str = ''
_all_edits_cache_proj_id: str = ""

# Build Shot filtered assets cache
_filtered_assets_list: List[Any] = []
_filtered_assets_cache_proj_id: str = ""
_filtered_assets_cache_shot_id: str = ""
_filtered_assets_cache_filter_type: str = ""
_filtered_assets_cache_scope_type: str = ""


def _addon_prefs_get(context: bpy.types.Context) -> bpy.types.AddonPreferences:
    """
    shortcut to get blender_kitsu addon preferences
    """
    root = __package__.split(".")[0]
    return context.preferences.addons[root].preferences


def user_active_get() -> User:
    global _user_active

    return _user_active


def project_active_get() -> Project:
    global _project_active

    return _project_active


def project_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _project_active

    _project_active = Project.by_id(entity_id)
    _addon_prefs_get(context).project_active_id = entity_id
    logger.debug("Set active project to %s", _project_active.name)


def project_active_reset(context: bpy.types.Context) -> None:
    global _project_active
    _project_active = Project()
    _addon_prefs_get(context).project_active_id = ""
    logger.debug("Reset active project")


def episode_active_get() -> Project:
    global _episode_active

    return _episode_active


def episode_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _episode_active

    _episode_active = Episode.by_id(entity_id)
    _addon_prefs_get(context).episode_active_id = entity_id
    logger.debug("Set active episode to %s", _episode_active.name)


def episode_active_reset_entity():
    global _episode_active
    _episode_active = Episode()


def episode_active_reset(context: bpy.types.Context) -> None:
    episode_active_reset_entity()
    context.scene.kitsu.episode_active_id = ""
    context.scene.kitsu.episode_active_name = ""
    logger.debug("Reset active episode")


def sequence_active_get() -> Sequence:
    return _sequence_active


def sequence_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _sequence_active

    _sequence_active = Sequence.by_id(entity_id)
    context.scene.kitsu.sequence_active_id = entity_id
    logger.debug("Set active sequence to %s", _sequence_active.name)


def sequence_active_reset_entity() -> None:
    global _sequence_active
    _sequence_active = Sequence()


def sequence_active_reset(context: bpy.types.Context) -> None:
    sequence_active_reset_entity()
    context.scene.kitsu.sequence_active_id = ""
    context.scene.kitsu.sequence_active_name = ""
    logger.debug("Reset active sequence")


def shot_active_get() -> Shot:
    global _shot_active

    return _shot_active


def shot_active_pull_update() -> Shot:
    global _shot_active
    Cache.clear_all()
    shot_active_id = bpy.context.scene.kitsu.shot_active_id
    _init_cache_entity(shot_active_id, Shot, "_shot_active", "shot")
    return _shot_active


def shot_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _shot_active

    _shot_active = Shot.by_id(entity_id)
    context.scene.kitsu.shot_active_id = entity_id
    logger.debug("Set active shot to %s", _shot_active.name)
    
    # Update build shot candidates when shot changes
    update_buildshot_candidates_for_active_shot(context)
    
    # Update build shot candidates when shot changes
    update_buildshot_candidates_for_active_shot(context)


def shot_active_reset_entity() -> None:
    global _shot_active
    _shot_active = Shot()


def shot_active_reset(context: bpy.types.Context) -> None:
    shot_active_reset_entity()
    context.scene.kitsu.shot_active_id = ""
    context.scene.kitsu.shot_active_name = ""
    logger.debug("Reset active shot")


def asset_active_get() -> Asset:
    global _asset_active

    return _asset_active


def asset_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _asset_active

    _asset_active = Asset.by_id(entity_id)
    context.scene.kitsu.asset_active_id = entity_id
    logger.debug("Set active asset to %s", _asset_active.name)


def asset_active_reset_entity() -> None:
    global _asset_active
    _asset_active = Asset()


def asset_active_reset(context: bpy.types.Context) -> None:
    asset_active_reset_entity()
    context.scene.kitsu.asset_active_id = ""
    context.scene.kitsu.asset_active_name = ""
    logger.debug("Reset active asset")


def asset_type_active_get() -> AssetType:
    global _asset_type_active

    return _asset_type_active


def asset_type_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _asset_type_active

    _asset_type_active = AssetType.by_id(entity_id)
    context.scene.kitsu.asset_type_active_id = entity_id
    logger.debug("Set active asset type to %s", _asset_type_active.name)

def asset_type_active_reset_entity() -> None:
    global _asset_type_active
    _asset_type_active = AssetType()


def asset_type_active_reset(context: bpy.types.Context) -> None:
    asset_type_active_reset_entity()
    context.scene.kitsu.asset_type_active_id = ""
    context.scene.kitsu.asset_type_active_name = ""
    logger.debug("Reset active asset type")


def task_type_active_get() -> TaskType:
    global _task_type_active

    return _task_type_active


def task_type_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _task_type_active

    _task_type_active = TaskType.by_id(entity_id)
    context.scene.kitsu.task_type_active_id = entity_id
    logger.debug("Set active task type to %s", _task_type_active.name)


def task_type_active_reset_entity() -> None:
    global _task_type_active
    _task_type_active = TaskType()


def task_type_active_reset(context: bpy.types.Context) -> None:
    task_type_active_reset_entity()
    context.scene.kitsu.task_type_active_id = ""
    context.scene.kitsu.task_type_active_name = ""
    logger.debug("Reset active task type")


def edit_active_set_by_id(context: bpy.types.Context, entity_id: str) -> None:
    global _edit_active

    _edit_active = Edit.by_id(entity_id)
    context.scene.kitsu.edit_active_id = entity_id
    logger.debug("Set active edit to %s", _task_type_active.name)


def edit_active_reset_entity() -> None:
    global _edit_active
    _edit_active = TaskType()


def edit_active_get() -> Project:
    global _edit_active

    return _edit_active


def task_type_active_reset(context: bpy.types.Context) -> None:
    edit_active_reset_entity()
    context.scene.kitsu.edit_active_id = ""
    context.scene.kitsu.edit_active_name = ""
    logger.debug("Reset active edit")


def get_projects_enum_list(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _projects_enum_list

    if not _addon_prefs_get(context).session.is_auth():
        return []

    projectlist = ProjectList()
    _projects_enum_list.clear()
    _projects_enum_list.extend([(p.id, p.name, p.description or "") for p in projectlist.projects])
    return _projects_enum_list


def get_episodes_enum_list(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _episodes_enum_list
    global _episode_cache_proj_id

    if not _addon_prefs_get(context).session.is_auth():
        return []

    project_active = project_active_get()
    if not project_active:
        return []

    # Return Cached list if project hasn't changed
    if _episode_cache_proj_id == project_active.id:
        return _episodes_enum_list

    # Update Cache Sequence ID
    _episode_cache_proj_id = project_active.id

    _episodes_enum_list.clear()
    _episodes_enum_list.extend(
        [(e.id, e.name, e.description or "") for e in project_active.get_episodes_all()]
    )
    return _episodes_enum_list


def get_sequences_enum_list(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _sequence_enum_list
    global _seq_cache_proj_id
    global _seq_cache_episode_id

    project_active = project_active_get()
    episode_active = episode_active_get()
    if not project_active:
        return []

    # Return Cached list if project hasn't changed
    if _seq_cache_proj_id == project_active.id and _seq_cache_episode_id == episode_active.id:
        return _sequence_enum_list

    # Update Cache Sequence ID
    _seq_cache_proj_id = project_active.id

    _sequence_enum_list.clear()

    if episode_active:
        _sequence_enum_list.extend(
            [(s.id, s.name, s.description or "") for s in episode_active.get_sequences_all()]
        )
    else:
        _sequence_enum_list.extend(
            [(s.id, s.name, s.description or "") for s in project_active.get_sequences_all()]
        )
    return _sequence_enum_list


def get_shots_enum_for_active_seq(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _shot_enum_list
    global _shot_cache_seq_id

    seq_active = sequence_active_get()

    if not seq_active:
        return []

    # Return Cached list if sequence hasn't changed
    if _shot_cache_seq_id == seq_active.id:
        return _shot_enum_list

    # Update Cache Sequence ID
    _shot_cache_seq_id = seq_active.id

    _shot_enum_list.clear()
    _shot_enum_list.extend(
        [(s.id, s.name, s.description or "") for s in seq_active.get_all_shots()]
    )
    return _shot_enum_list


def get_shots_enum_for_seq(
    self: bpy.types.Operator, context: bpy.types.Context, sequence: Sequence
) -> List[Tuple[str, str, str]]:
    global _shot_enum_list

    _shot_enum_list.clear()
    _shot_enum_list.extend([(s.id, s.name, s.description or "") for s in sequence.get_all_shots()])
    return _shot_enum_list


def get_filtered_assets_for_buildshot(context: bpy.types.Context, asset_filter: str = 'ALL', asset_scope: str = 'PROJECT') -> List[Any]:
    """Get filtered assets for build_shot with caching.
    
    Caches assets by project/shot and filter type to avoid recalculation during UI rendering and search.
    Can filter by asset type and choose between project-wide or shot-specific assets.
    
    Args:
        context: Blender context
        asset_filter: Filter type - 'ALL', 'CHR', 'PRP', 'SET', 'ITM'
        asset_scope: Asset scope - 'PROJECT' for all project assets, 'SHOT' for shot-specific assets
        
    Returns:
        List of filtered asset objects
    """
    global _filtered_assets_list
    global _filtered_assets_cache_proj_id
    global _filtered_assets_cache_shot_id
    global _filtered_assets_cache_filter_type
    global _filtered_assets_cache_scope_type
    
    project_active = project_active_get()
    shot_active = shot_active_get() if asset_scope == 'SHOT' else None
    
    # Determine cache key based on scope
    scope_id = shot_active.id if asset_scope == 'SHOT' else project_active.id
    
    # Return cached list if project/shot, filter, and scope haven't changed
    if (_filtered_assets_cache_proj_id == project_active.id and 
        _filtered_assets_cache_shot_id == (shot_active.id if asset_scope == 'SHOT' else "") and
        _filtered_assets_cache_filter_type == asset_filter and
        _filtered_assets_cache_scope_type == asset_scope):
        return _filtered_assets_list
    
    # Update cache identifiers
    _filtered_assets_cache_proj_id = project_active.id
    _filtered_assets_cache_shot_id = shot_active.id if asset_scope == 'SHOT' else ""
    _filtered_assets_cache_filter_type = asset_filter
    _filtered_assets_cache_scope_type = asset_scope
    
    _filtered_assets_list.clear()
    
    # Get assets based on scope
    if asset_scope == 'SHOT':
        if not shot_active or not shot_active.id:
            return _filtered_assets_list
        all_assets = shot_active.get_all_assets()
    else:  # PROJECT
        if not project_active or not project_active.id:
            return _filtered_assets_list
        all_assets = project_active.get_all_assets()
    
    if asset_filter == 'ALL':
        for asset in all_assets:
            asset_type = asset.name.split('_')[1] if len(asset.name.split('_')) > 1 else None
            if asset_type in ['CHR', 'PRP', 'SET', 'ITM']:
                _filtered_assets_list.append(asset)
        return _filtered_assets_list
    
    # Filter by asset type
    for asset in all_assets:
        asset_type = asset.name.split('_')[1] if len(asset.name.split('_')) > 1 else None
        if asset_filter == 'CHR' and asset_type == 'CHR':
            _filtered_assets_list.append(asset)
        elif asset_filter == 'PRP' and asset_type == 'PRP':
            _filtered_assets_list.append(asset)
        elif asset_filter == 'SET' and asset_type == 'SET':
            _filtered_assets_list.append(asset)
        elif asset_filter == 'ITM' and asset_type == 'ITM':
            _filtered_assets_list.append(asset)
    
    return _filtered_assets_list


def get_assetypes_enum_list(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _asset_types_enum_list
    global _asset_cache_proj_id

    project_active = project_active_get()
    if not project_active:
        return []

    # Return Cached list if project hasn't changed
    if _asset_cache_proj_id == project_active.id:
        return _asset_types_enum_list

    # Update Cache Sequence ID
    _asset_cache_proj_id = project_active.id

    _asset_types_enum_list.clear()
    _asset_types_enum_list.extend(
        [(at.id, at.name, "") for at in project_active.get_all_asset_types()]
    )
    return _asset_types_enum_list


def get_assets_enum_for_active_asset_type(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _asset_enum_list
    global _asset_cache_asset_type_id

    project_active = project_active_get()
    asset_type_active = asset_type_active_get()
    episode_active = episode_active_get()

    if not project_active or not asset_type_active:
        return []

    if _asset_cache_asset_type_id == asset_type_active.id:
        return _asset_enum_list

    _asset_cache_asset_type_id = asset_type_active.id

    all_assets = project_active.get_all_assets_for_type(asset_type_active)

    _asset_enum_list.clear()
    if not episode_active:
        _asset_enum_list.extend([(a.id, a.name, a.description or "") for a in all_assets])
    else:
        episode_assets = filter(
            lambda p: p.source_id == episode_active.id or p.source_id is None, all_assets
        )
        _asset_enum_list.extend([(a.id, a.name, a.description or "") for a in episode_assets])
    return _asset_enum_list


def _get_priority_value(task_type: TaskType) -> Union[int, float]:
    """Extract priority value from TaskType object.
    
    Handles both attribute and dict-like access patterns for compatibility.
    Lower values sort first, items without priority sort to end.
    
    Args:
        task_type: TaskType object to extract priority from
        
    Returns:
        Priority as int, or inf if not available
    """
    try:
        # Try attribute access first (dataclass standard)
        priority = getattr(task_type, 'priority', None)
        if priority is not None:
            return int(priority)
    except (AttributeError, TypeError, ValueError):
        pass
    
    # No priority found, sort to end
    return float('inf')


def _reorder_task_types_by_priority(task_types: List[TaskType]) -> List[TaskType]:
    """Sort task types by priority attribute.
    
    Lower priority values appear first. Items without priority appear last.
    
    Args:
        task_types: List of TaskType objects to sort
        
    Returns:
        List of TaskType objects sorted by priority (ascending)
    """
    return sorted(
        task_types,
        key=_get_priority_value
    )


def get_task_types_enum_for_current_context(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _task_types_enum_list
    global _project_active

    # Import within function to avoid circular import
    from .context import core as context_core

    task_types = []
    if context_core.is_shot_context():
        task_types = [
            t
            for t in TaskType.all_shot_task_types()
            if t.id in _project_active.task_types
        ]

    if context_core.is_asset_context():
        task_types = [
            t
            for t in TaskType.all_asset_task_types()
            if t.id in _project_active.task_types
        ]

    if context_core.is_sequence_context():
        task_types = [
            t
            for t in TaskType.all_sequence_task_types()
            if t.id in _project_active.task_types
        ]

    if context_core.is_edit_context():
        task_types = [
            t
            for t in TaskType.all_edit_task_types()
            if t.id in _project_active.task_types
        ]

    # Sort by priority
    sorted_task_types = _reorder_task_types_by_priority(task_types)
    items = [(t.id, t.name, "") for t in sorted_task_types]

    _task_types_enum_list.clear()
    _task_types_enum_list.extend(items)

    return _task_types_enum_list


def get_shot_task_types_enum(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    # Returns all avaliable task types across all shots in the current project
    global _task_types_shots_enum_list
    global _all_shot_tasks_cache_proj_id

    project_active = project_active_get()

    # Return Cached list if project hasn't changed
    if _all_shot_tasks_cache_proj_id == project_active.id:
        return _task_types_shots_enum_list

    # Update Cache project ID
    _all_shot_tasks_cache_proj_id = project_active.id

    task_types = [t for t in TaskType.all_shot_task_types() if t.id in project_active.task_types]
    sorted_task_types = _reorder_task_types_by_priority(task_types)
    items = [(t.id, t.name, "") for t in sorted_task_types]

    _task_types_shots_enum_list.clear()
    _task_types_shots_enum_list.extend(items)

    return _task_types_shots_enum_list


def get_shot_task_types_enum_for_shot(  # TODO Rename
    self: bpy.types.Operator, context: bpy.types.Context, shot: Shot
) -> List[Tuple[str, str, str]]:
    global _task_types_shots_enum_list
    global _task_type_cache_shot_id

    # Return Cached list if shot hasn't changed
    if _task_type_cache_shot_id == shot.id:
        return _task_types_shots_enum_list

    # Update Cache Sequence ID
    _task_type_cache_shot_id = shot.id

    task_types = shot.get_all_task_types()
    sorted_task_types = _reorder_task_types_by_priority(task_types)
    items = [(t.id, t.name, "") for t in sorted_task_types]

    _task_types_shots_enum_list.clear()
    _task_types_shots_enum_list.extend(items)

    return _task_types_shots_enum_list


def get_all_edits_enum_for_active_project(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _project_active
    global _all_edits_cache_proj_id
    global _all_edits_enum_list

    if _all_edits_cache_proj_id == _project_active.id:
        return _all_edits_enum_list

    # Update Cache Project ID
    _all_edits_cache_proj_id = _project_active.id

    items = [(t.id, t.name, "") for t in _project_active.get_all_edits()]

    _all_edits_enum_list.clear()
    _all_edits_enum_list.extend(items)

    return _all_edits_enum_list


def get_all_task_statuses_enum(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _task_statuses_enum_list
    global _all_task_type_cache_proj_id

    project_active = project_active_get()

    # Return Cached list if project hasn't changed
    if _all_task_type_cache_proj_id == project_active.id:
        return _task_statuses_enum_list

    # Update Cache project ID
    _all_task_type_cache_proj_id = project_active.id

    items = [(t.id, t.name, "") for t in TaskStatus.all_task_statuses()]

    _task_statuses_enum_list.clear()
    _task_statuses_enum_list.extend(items)

    return _task_statuses_enum_list


def load_user_all_tasks(context: bpy.types.Context) -> List[Task]:
    global _user_all_tasks
    global _user_active

    tasks = _user_active.all_tasks_to_do()
    _user_all_tasks.clear()
    _user_all_tasks.extend(tasks)

    _update_tasks_collection_prop(context)

    logger.debug("Loaded assigned tasks for: %s", _user_active.full_name)

    return _user_all_tasks


def _update_tasks_collection_prop(context: bpy.types.Context) -> None:
    global _user_all_tasks
    addon_prefs = _addon_prefs_get(bpy.context)
    tasks_coll_prop = addon_prefs.tasks

    # Get current index.
    idx = context.window_manager.kitsu.tasks_index

    # Clear all old tasks.
    tasks_coll_prop.clear()

    # Populate with new tasks.
    for task in _user_all_tasks:
        item = tasks_coll_prop.add()
        item.id = task.id
        item.entity_id = task.entity_id
        item.entity_name = task.entity_name
        item.task_type_id = task.task_type_id
        item.task_type_name = task.task_type_name

    # Update index.
    idx = len(tasks_coll_prop) - 1


def get_user_all_tasks_enum(
    self: bpy.types.Operator, context: bpy.types.Context
) -> List[Tuple[str, str, str]]:
    global _user_all_tasks_enum_list
    global _user_all_tasks

    enum_items = [(t.id, t.name, "") for t in _user_all_tasks]

    _user_all_tasks_enum_list.clear()
    _user_all_tasks_enum_list.extend(enum_items)

    return _user_all_tasks_enum_list


def get_user_all_tasks() -> List[Task]:
    global _user_all_tasks
    return _user_all_tasks


def _init_cache_entity(
    entity_id: str, entity_type: Any, cache_variable_name: Any, cache_name: str
) -> None:
    if entity_id:
        try:
            globals()[cache_variable_name] = entity_type.by_id(entity_id)
            logger.debug(
                "Initiated active %s cache to: %s",
                cache_name,
                globals()[cache_variable_name].name,
            )
        except gazu.exception.RouteNotFoundException:
            logger.error(
                "Failed to initialize active %s cache. ID not found on server: %s",
                cache_name,
                entity_id,
            )


def init_startup_variables(context: bpy.types.Context) -> None:
    addon_prefs = _addon_prefs_get(context)
    global _cache_startup_initialized
    global _user_active
    global _user_all_tasks

    if not addon_prefs.session.is_auth():
        logger.debug("Skip initiating startup cache. Session not authorized")
        return

    if _cache_startup_initialized:
        logger.debug("Startup Cache already initiated")
        return

    # User.
    _user_active = User()
    logger.debug("Initiated active user cache to: %s", _user_active.full_name)

    # User Tasks.
    load_user_all_tasks(context)
    logger.debug("Initiated active user tasks")

    _cache_startup_initialized = True


def clear_startup_variables():
    global _user_active
    global _user_all_tasks
    global _cache_startup_initialized

    _user_active = User()
    logger.debug("Cleared active user cache")

    _user_all_tasks.clear()
    _update_tasks_collection_prop(bpy.context)
    logger.debug("Cleared active user all tasks cache")

    _cache_startup_initialized = False


def init_cache_variables() -> None:
    global _project_active
    global _episode_active
    global _sequence_active
    global _shot_active
    global _asset_active
    global _asset_type_active
    global _task_type_active
    global _cache_initialized
    addon_prefs = _addon_prefs_get(bpy.context)

    if not addon_prefs.session.is_auth():
        logger.debug("Skip initiating cache. Session not authorized")
        return

    if _cache_initialized:
        logger.debug("Cache already initiated")
        return

    project_active_id = addon_prefs.project_active_id
    episode_active_id = bpy.context.scene.kitsu.episode_active_id
    sequence_active_id = bpy.context.scene.kitsu.sequence_active_id
    shot_active_id = bpy.context.scene.kitsu.shot_active_id
    asset_active_id = bpy.context.scene.kitsu.asset_active_id
    asset_type_active_id = bpy.context.scene.kitsu.asset_type_active_id
    task_type_active_id = bpy.context.scene.kitsu.task_type_active_id

    _init_cache_entity(project_active_id, Project, "_project_active", "project")
    _init_cache_entity(episode_active_id, Episode, "_episode_active", "episode")
    _init_cache_entity(sequence_active_id, Sequence, "_sequence_active", "sequence")
    _init_cache_entity(asset_type_active_id, AssetType, "_asset_type_active", "asset type")
    _init_cache_entity(shot_active_id, Shot, "_shot_active", "shot")
    _init_cache_entity(asset_active_id, Asset, "_asset_active", "asset")
    _init_cache_entity(task_type_active_id, TaskType, "_task_type_active", "task type")

    _cache_initialized = True


def clear_cache_variables():
    global _project_active
    global _episode_active
    global _sequence_active
    global _shot_active
    global _asset_active
    global _asset_type_active
    global _task_type_active
    global _cache_initialized

    _user_active = User()
    logger.debug("Cleared active user cache")

    _shot_active = Shot()
    logger.debug("Cleared active shot cache")

    _asset_active = Asset()
    logger.debug("Cleared active asset cache")

    _sequence_active = Sequence()
    logger.debug("Cleared active aequence cache")

    _asset_type_active = AssetType()
    logger.debug("Cleared active asset type cache")

    _project_active = Project()
    logger.debug("Cleared active project cache")

    _task_type_active = TaskType()
    logger.debug("Cleared active task type cache")

    _cache_initialized = False


@persistent
def load_post_handler_update_cache(dummy: Any) -> None:
    clear_cache_variables()
    init_cache_variables()


@persistent
def load_post_handler_init_startup_variables(dummy: Any) -> None:
    init_startup_variables(bpy.context)


# ----------BUILD SHOT PROPERTIES----------


def clear_buildshot_properties() -> None:
    """Remove dynamic BoolProperties created for build_shot assets."""
    for prop in list(dir(bpy.types.Scene)):
        if prop.startswith("buildshot_"):
            try:
                delattr(bpy.types.Scene, prop)
            except Exception:
                pass


def update_buildshot_candidates_for_active_shot(context: bpy.types.Context) -> None:
    """Update build_shot_candidates properties when active shot changes.
    
    This is automatically called from shot_active_set_by_id as part of the
    Kitsu cache system, not from external operators. It creates dynamic BoolProperties
    for each asset in the selected shot and stores candidate names in the Kitsu props.
    """
    scene = context.scene
    kitsu_scene = scene.kitsu
    
    # Clear previous asset BoolProperties
    clear_buildshot_properties()
    
    # Clear candidates list
    if hasattr(kitsu_scene, 'build_shot_candidate_names'):
        kitsu_scene.build_shot_candidate_names.clear()

    shot_active = shot_active_get()
    if not shot_active or not shot_active.id:
        return

    try:
        assets = shot_active.get_all_assets()
    except Exception:
        logger.warning("Failed to retrieve assets for active shot")
        return

    if not assets:
        return

    # Create dynamic BoolProperties for each asset and store candidate names
    for asset in assets:
        # Create dynamic BoolProperty for asset selection
        prop_name = f"buildshot_{asset.name}"
        setattr(
            bpy.types.Scene,
            prop_name,
            bpy.props.BoolProperty(
                name=asset.name,
                default=True
            )
        )
        
        # Store in Kitsu props for reference
        if hasattr(kitsu_scene, 'build_shot_candidate_names'):
            item = kitsu_scene.build_shot_candidate_names.add()
            item.name = asset.name


def update_scene_buildshot_properties(scene: bpy.types.Scene) -> None:
    """Deprecated: Use Kitsu cache system instead.
    
    This function is kept for backward compatibility but should not be called directly.
    Build shot candidates are now automatically updated via the Kitsu cache system
    when the active shot changes (via shot_active_set_by_id).
    
    The architecture now follows:
    - kitsu/cache.py: Shot change detection and update logic
    - kitsu/props.py: Property storage in KITSU_property_group_scene
    - No external operator dependency
    """
    logger.warning(
        "update_scene_buildshot_properties is deprecated. "
        "Build shot candidates are now managed automatically by the Kitsu cache system."
    )
    # For backward compatibility, delegate to the new function
    if hasattr(scene, 'kitsu'):
        update_buildshot_candidates_for_active_shot(bpy.context)


# ---------REGISTER ----------.


def register():
    # Handlers.
    bpy.app.handlers.load_post.append(load_post_handler_update_cache)
    bpy.app.handlers.load_post.append(load_post_handler_init_startup_variables)


def unregister():
    # Clear handlers.
    bpy.app.handlers.load_post.remove(load_post_handler_init_startup_variables)
    bpy.app.handlers.load_post.remove(load_post_handler_update_cache)
