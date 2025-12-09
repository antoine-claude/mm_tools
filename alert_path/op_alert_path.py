import bpy

class CHECKPATH_OT_show_popup(bpy.types.Operator):
    bl_idname = "wm.check_project_path_popup"
    bl_label = "Chemin incorrect"

    message: bpy.props.StringProperty()

    def invoke(self, context, event=None):

        lines = self.message.split("\n")

        def draw(menu_self, context):
            for line in lines:
                menu_self.layout.label(text=line)

        context.window_manager.popup_menu(
            draw,
            title="Avertissement",
            icon="ERROR"
        )
        return {'FINISHED'}

