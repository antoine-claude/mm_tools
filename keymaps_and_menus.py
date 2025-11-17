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

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)

    # Supprime les raccourcis existants pour 'S' si nécessaire
    for km_item in km.keymap_items:
        if km_item.type == 'S':
            km.keymap_items.remove(km_item)

    # Ajoute les nouveaux raccourcis
    km.keymap_items.new('wm.save_mainfile_with_absolute_paths', 'S', 'PRESS', ctrl=True)
    km.keymap_items.new('wm.save_mainfile_incremental', 'S', 'PRESS', shift=True, ctrl=True)

    addon_keymaps.append((km, km.keymap_items[-1]))  # Stocke les keymaps pour unregister

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

