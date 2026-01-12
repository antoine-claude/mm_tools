import bpy
import gazu
_cached_tasks = [("NONE", "-- Select a task --", "")]
ADDON_NAME = "mm_tools"


# --------------------------------------------------
# CONTEXT HELPERS
# --------------------------------------------------

def get_active_project():
    prefs = bpy.context.preferences.addons[ADDON_NAME].preferences
    if prefs.project_id == "NONE":
        return None
    return gazu.project.get_project(prefs.project_id)


def get_current_shot():
    filepath = bpy.path.basename(bpy.data.filepath)
    parts = filepath.split("_")
    if len(parts) < 4:
        return None

    episode_name = parts[1]
    shot_name = parts[3]

    project = get_active_project()
    if not project:
        return None

    episodes = gazu.context.all_episodes_for_project(project)
    episode = next((e for e in episodes if e["name"] == episode_name), None)
    if not episode:
        return None

    shots = gazu.shot.all_shots_for_episode(episode)
    return next((s for s in shots if s["name"] == shot_name), None)


# TASK ENUM


def load_tasks_for_project(project_id):
    global _cached_tasks

    if project_id == "NONE":
        _cached_tasks = [("NONE", "-- Select a task --", "")]
        return

    shot = get_current_shot()
    if not shot:
        _cached_tasks = [("NONE", "-- Select a task --", "")]
        return

    tasks = gazu.task.all_tasks_for_shot(shot)
    _cached_tasks = [("NONE", "-- Select a task --", "")]
    for task in tasks:
        _cached_tasks.append(
            (task["id"], task["task_type_name"], task["task_type_name"])
        )


def get_tasks_enum(self, context):
    return _cached_tasks


# --------------------------------------------------
# OPERATOR
# --------------------------------------------------

class KITSU_OT_Playblast(bpy.types.Operator):
    bl_idname = "kitsu.playblast"
    bl_label = "Playblast & Send to Kitsu"

    def execute(self, context):
        shot = get_current_shot()
        if not shot:
            self.report({'ERROR'}, "No shot found")
            return {'CANCELLED'}
        
        tasks = gazu.task.all_tasks_for_shot(shot)
        for task in tasks:
            if task["id"] == context.scene.kitsu_playblast_task:
                task_id = task
                break
            
        if task_id == "NONE":
            self.report({'ERROR'}, "No task selected")
            return {'CANCELLED'}


        # Logique pour le playblast et l'envoi vers Kitsu
        bpy.ops.render.opengl(animation=True, view_context=False)

        # publish du preview/playblast vers Kitsu avec le statut WIP
        comment = bpy.context.scene.get("comment_playblast", "")
        preview_file_path = bpy.context.scene.render.filepath
        #task_status (str / dict) – The task status dict or ID. 
        task_status = gazu.task.get_task_status_by_short_name("wip")
        if task_id and preview_file_path:
            try:
                # Publier l'aperçu
                gazu.task.publish_preview(
                    task=task_id,
                    comment=comment,
                    preview_file_path=preview_file_path,
                    task_status=task_status
                )
                print("Preview published successfully.")
            except Exception as e:
                print(f"Error publishing preview: {e}")
        else:
            print("Task ID or preview file path is missing.")

        self.report({'INFO'}, "Playblast sent to Kitsu")   

        return {'FINISHED'}


# --------------------------------------------------
# PANEL
# --------------------------------------------------

class KITSU_PT_PlayblastPanel(bpy.types.Panel):
    bl_label = "Kitsu Playblast"
    bl_idname = "KITSU_PT_playblast"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Kitsu"

    bpy.types.Scene.comment_playblast = bpy.props.StringProperty(
        name="Commentaire",
        description="Commentaire pour le post commment du playblast",
        default=""
    )

    def draw(self, context):
        layout = self.layout
        shot = get_current_shot()

        if not shot:
            layout.label(text="No shot selected or file not saved.")
            return

        layout.prop(context.scene, "kitsu_playblast_task", text="Task")
        layout.prop(context.scene, "comment_playblast", text="Comment")
        layout.operator("kitsu.playblast", text="Playblast & Send to Kitsu", icon='RENDER_ANIMATION')


# --------------------------------------------------
# PROPERTIES
# --------------------------------------------------

def register_properties():
    bpy.types.Scene.kitsu_playblast_task = bpy.props.EnumProperty(
        name="Task",
        items=get_tasks_enum,
    )


def unregister_properties():
    if hasattr(bpy.types.Scene, "kitsu_playblast_task"):
        del bpy.types.Scene.kitsu_playblast_task


# --------------------------------------------------
# HANDLERS
# --------------------------------------------------

@bpy.app.handlers.persistent
def load_tasks_on_file_load(dummy):
    try:
        prefs = bpy.context.preferences.addons[ADDON_NAME].preferences
        load_tasks_for_project(prefs.project_id)
    except Exception:
        pass


# --------------------------------------------------
# EXPORTS
# --------------------------------------------------

classes = (
    KITSU_OT_Playblast,
    KITSU_PT_PlayblastPanel,
)

def get_classes():
    return classes

def get_handlers():
    return [load_tasks_on_file_load]
