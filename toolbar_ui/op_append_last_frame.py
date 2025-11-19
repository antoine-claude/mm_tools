import bpy
from pathlib import Path

class WM_OT_append_previous_frame(bpy.types.Operator):
    bl_idname = "view3d.mm_append_previous_frame"
    bl_label = "append last frame from previous shot"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected_armature = None
        try:
            if bpy.context.active_object is None or bpy.context.active_object.type != "ARMATURE":
                raise Exception("Veuillez sélectionner une armature !")
            else:
                selected_armature = bpy.context.active_object
                print(f"Armature sélectionnée : {selected_armature.name}")

        except Exception as e:
            def draw(self, context):
                self.layout.label(text=str(e))
            bpy.context.window_manager.popup_menu(draw, title="Erreur", icon='ERROR')

        # --- Fonction pour importer toutes les actions depuis un autre fichier ---
        def append_all_actions_from_blend(file_path, target_directory):
            """
            Append all actions from a specified blend file.
            
            :param file_path: Path to the blend file (e.g., 'path/to/file.blend')
            :param target_directory: Directory within the blend file (e.g., 'Action')
            """
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"Le fichier {file_path} n'existe pas.")
                return []

            try:
                with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
                    actions = data_from.actions[:]
                    print("Actions trouvées :", actions)
            except Exception as e:
                print("Erreur lors du chargement des actions :", e)
                return []

            appended_actions = []
            for action_name in actions:
                directory = str(file_path) + target_directory
                try:
                    bpy.ops.wm.append(directory=directory, filename=action_name)
                    appended_actions.append(action_name)
                except Exception as e:
                    print(f"Erreur lors de l'import de l'action {action_name} :", e)

            return appended_actions

        # --- Traitement si une armature est sélectionnée ---
        if selected_armature:
            active_file = bpy.data.filepath
            past_folder = Path(active_file).parents[2] / (Path(active_file).parents[1].name[:-2] + "10") / Path(active_file).parent.name
            version = Path(active_file).name.split("_")[-2]

            past_file = None
            for file in past_folder.glob("*.blend"):
                file_version = file.name.split("_")[-2]
                if file_version.startswith("v") and file_version[1:].isdigit():
                    if int(file_version[1:]) > int(version[1:]):
                        past_file = file
                        version = file_version
                        print("Fichier précédent trouvé :", past_file)

            if past_file:
                appended_actions = append_all_actions_from_blend(past_file, "/Action/")
                if appended_actions:
                    for action in bpy.data.actions:
                        last_frame = action.frame_range[1]
                        for fcurve in action.fcurves:
                            for keyframe in fcurve.keyframe_points:
                                keyframe.co.x -= last_frame - 1
                        print(f"Action {action.name} importée depuis {past_file.name} et deplacé au debut")
            else:
                print("Aucun fichier précédent trouvé pour importer les actions.")
                        
        return {'FINISHED'}


classes = [WM_OT_append_previous_frame]