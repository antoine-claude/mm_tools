"""
Kitsu addon for mm_tools.
Provides integration with Kitsu for playblast rendering and task management.
"""

import importlib
from . import context, build_shot, build_asset, prefs, props, auth, playblast, generic

# ---------- REGISTRATION ----------


def reload():
    global auth
    global playblast
    global context
    global build_shot
    global build_asset
    global prefs
    global props
    global generic

    auth = importlib.reload(auth)
    playblast = importlib.reload(playblast)
    context = importlib.reload(context)
    build_shot = importlib.reload(build_shot)
    build_asset = importlib.reload(build_asset)
    prefs = importlib.reload(prefs)
    props = importlib.reload(props)
    generic = importlib.reload(generic)

def register():
    """Register all Kitsu components."""
    auth.register()
    context.register()
    generic.register()
    props.register()
    prefs.register()
    build_asset.register()
    build_shot.register()
    playblast.register()


def unregister():
    """Unregister all Kitsu components."""
    playblast.unregister()
    build_shot.unregister()
    build_asset.unregister()
    prefs.unregister()
    props.unregister()
    generic.unregister()
    context.unregister()
    auth.unregister()


# # ---------- CLASSES ----------

# def get_kitsu_classes():
#     """Get all Kitsu-related classes for registration."""
#     classes = []
#     # Classes are registered via register() functions in each module
#     return classes


# # ---------- PROPERTIES ----------

# def register_kitsu_properties():
#     """Register Kitsu scene properties."""
#     playblast.register_properties()


# def unregister_kitsu_properties():
#     """Unregister Kitsu scene properties."""
#     playblast.unregister_properties()

