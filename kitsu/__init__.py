import bpy

from . import kitsu_login_topbar
from . import kitsu_playblast

# ---------- CLASSES ----------

def get_kitsu_classes():
    classes = []
    classes.extend(kitsu_login_topbar.get_classes())
    classes.extend(kitsu_playblast.get_classes())
    return classes


# ---------- HANDLERS ----------

def ensure_kitsu_handlers():
    # timers
    bpy.app.timers.register(kitsu_login_topbar.initial_kitsu_check, first_interval=0.1)

    # file load handlers
    for h in kitsu_playblast.get_handlers():
        if h not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(h)


def remove_kitsu_handlers():
    for h in kitsu_playblast.get_handlers():
        if h in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(h)


# ---------- UI ----------

def register_kitsu_ui():
    for draw in kitsu_login_topbar.get_draw_funcs():
        bpy.types.TOPBAR_MT_editor_menus.append(draw)


def unregister_kitsu_ui():
    for draw in kitsu_login_topbar.get_draw_funcs():
        bpy.types.TOPBAR_MT_editor_menus.remove(draw)


# ---------- PROPERTIES ----------

def register_kitsu_properties():
    kitsu_playblast.register_properties()


def unregister_kitsu_properties():
    kitsu_playblast.unregister_properties()
