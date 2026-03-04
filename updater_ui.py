"""
Addon preferences UI and registration.
This module handles the preferences display for the updater.
The main AddonPreferences class is defined in prefs.py to avoid duplication.
"""

import bpy
from . import addon_updater_ops
from .kitsu import prefs


# Register preferences from prefs module
classes = prefs.classes


def register():
    """Register addon components."""
    # Preferences are registered in __init__.py
    # This function is kept for compatibility with addon registration system
    pass


def unregister():
    """Unregister addon components."""
    # Preferences are unregistered in __init__.py
    pass