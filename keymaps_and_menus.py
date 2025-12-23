import bpy

addon_keymaps = []

def custom_file_menu_draw(self, context):
    """Custom draw function for the File menu to include the incremental save option."""
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    layout.menu("TOPBAR_MT_file_new", text="New", icon='FILE_NEW')
    layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')
    layout.menu("TOPBAR_MT_file_open_recent")
    layout.operator("wm.revert_mainfile")
    layout.menu("TOPBAR_MT_file_recover")
    layout.separator()

    layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
    layout.operator("wm.save_mainfile_with_absolute_paths", text="Save", icon='FILE_TICK')
    layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
    layout.operator("wm.save_mainfile_incremental", text="Save Incremental", icon='FILE_TICK')
    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.save_as_mainfile", text="Save As", icon='FILE_TICK')
    layout.separator()

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.link", text="Link...", icon='LINK_BLEND')
    layout.operator("wm.append", text="Append...", icon='APPEND_BLEND')
    layout.menu("TOPBAR_MT_file_previews")
    layout.separator()

    layout.menu("TOPBAR_MT_file_import", icon='IMPORT')
    layout.menu("TOPBAR_MT_file_export", icon='EXPORT')
    layout.separator()

    layout.menu("TOPBAR_MT_file_external_data")
    layout.menu("TOPBAR_MT_file_cleanup")
    layout.separator()

    layout.menu("TOPBAR_MT_file_defaults")
    layout.separator()

    layout.operator("wm.quit_blender", text="Quit", icon='QUIT')

addon_keymaps = []  # on stocke seulement les ID

REGISTERED_KEYMAP_IDS = [
    "wm.save_mainfile_with_absolute_paths",
    "wm.save_mainfile_incremental"
]

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    if kc is None:
        return

    km = kc.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')

    # Supprimer les anciens raccourcis "S"
    remove_list = [kmi for kmi in km.keymap_items if kmi.type == 'S']
    for kmi in remove_list:
        try:
            km.keymap_items.remove(kmi)
        except:
            pass

    # Ajouter les keymaps voulus
    km.keymap_items.new(
        REGISTERED_KEYMAP_IDS[0], 'S', 'PRESS', ctrl=True
    )
    km.keymap_items.new(
        REGISTERED_KEYMAP_IDS[1], 'S', 'PRESS', shift=True, ctrl=True
    )
    #Ajouter Ctrl Q pour wm.quit_blender
    km.keymap_items.new(
        "wm.quit_blender", 'Q', 'PRESS', ctrl=True
    )

    addon_keymaps.append(("Window", km.name))



def unregister_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    for km_name, km_id in addon_keymaps:
        km = kc.keymaps.get(km_name)
        if not km:
            continue

        # Supprimer uniquement les keymaps ajoutés par l’addon
        for kmi in list(km.keymap_items):
            if kmi.idname in REGISTERED_KEYMAP_IDS:
                try:
                    km.keymap_items.remove(kmi)
                except RuntimeError:
                    pass
                except KeyError:
                    pass

    addon_keymaps.clear()