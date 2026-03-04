"""
Kitsu addon for mm_tools.
Provides integration with Kitsu for playblast rendering and task management.
"""

import bpy
import importlib
from . import shot_build, prefs, props, auth, playblast, generic

# ---------- REGISTRATION ----------


def reload():
    global auth
    global playblast
    global shot_build
    global prefs
    global props
    global generic

    auth = importlib.reload(auth)
    playblast = importlib.reload(playblast)
    shot_build = importlib.reload(shot_build)
    prefs = importlib.reload(prefs)
    props = importlib.reload(props)
    generic = importlib.reload(generic)

def register():
    """Register all Kitsu components."""
    props.register()
    auth.register()
    generic.register()
    playblast.register()
    shot_build.register()
    prefs.register()


def unregister():
    """Unregister all Kitsu components."""
    auth.unregister()
    generic.unregister()
    playblast.unregister()
    shot_build.unregister()
    prefs.unregister()
    props.unregister()


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

