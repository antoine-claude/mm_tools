from . import dependencies

dependencies.preload_modules()

import bpy
from . import kitsu
from . import (lighting, alert_path, anim_utils, frustum_vis, playblast_copy_montage)
from . import addon_updater_ops

# from . import updater_ui
import importlib
# importlib.reload(updater_ui)

bl_info = {
    "name": "MM Tools",
    "author": "Antoine C",
    "version": (0, 0, 8, 50),
}


def register():
    """Register all addon components."""
    addon_updater_ops.register(bl_info)
    alert_path.register()
    anim_utils.register()
    frustum_vis.register()
    lighting.register()
    playblast_copy_montage.register()
    kitsu.register()


def unregister():
    """Unregister all addon components."""
    # Unregister properties first
    playblast_copy_montage.unregister()
    lighting.unregister()
    frustum_vis.unregister()
    anim_utils.unregister()
    alert_path.unregister()
    addon_updater_ops.unregister()
    # Unregister Kitsu module
    kitsu.unregister()