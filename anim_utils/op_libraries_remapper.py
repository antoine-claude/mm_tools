import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from pathlib import Path
import os


# --- Définition de la structure de données ---
class RemapItem(PropertyGroup):
    select: BoolProperty(name="Select", default=False)
    lib_name: StringProperty()
    path: StringProperty()
    new_path: StringProperty()
    is_missing: StringProperty()


# --- L'opérateur principal ---
class OT_RemapPaths(Operator):
    bl_idname = "view3d.mm_libraries_remapper"
    bl_label = "Libraries Remapper"
    bl_options = {'REGISTER', 'UNDO'}

    remap_items: CollectionProperty(type=RemapItem)

    def invoke(self, context, event):
        self.remap_items.clear()
        racine = Path("R:/")

        # Collecte des bibliothèques non conformes
        for lib in bpy.data.libraries:
            if not lib.filepath.startswith("R:"):
                print(lib.filepath)
                item = self.remap_items.add()
                item.path = lib.filepath
                item.lib_name = lib.name
                item.is_missing = 'MISSING' if lib.is_missing else ''

                source = Path(lib.filepath)
                parts = source.parts

                # Exemple : recalcul d’un chemin cible
                if "melodyandmomon" in parts:
                    idx = parts.index("melodyandmomon")
                    subpath = Path(*parts[idx:])
                    dest = racine / subpath
                    item.new_path = str(dest)
                    print("new path :",item.new_path)
                if "Assets" in parts :
                    idx = parts.index("Assets")
                    print("idx :", idx)
                    subpath = Path(*parts[idx:])
                    print("subpath",subpath)
                    dest = racine /"melodyandmomon"/ subpath
                    print("dest :", dest)
                    item.new_path = str(dest)
                    print("new path :",item.new_path)
                else:
                    item.new_path = "<non trouvé>"

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=900)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Libraries to Remap:", icon="FILE_FOLDER")

        col = layout.column(align=True)
        for item in self.remap_items:
            row = col.row(align=True)
            row.prop(item, "select", text="")  # ✅ Checkbox booléenne
            row.label(text=item.path, icon="LIBRARY_DATA_DIRECT")
            row.label(text="→")
            row.label(text=item.new_path)  # ✅ Champ éditable (nouveau chemin)
            if item.is_missing:
                row.label(text=item.is_missing, icon="ERROR")

    def execute(self, context):
        # Parcourt toutes les lignes cochées
        for item in self.remap_items:
            if item.select:
                if item.new_path and os.path.exists(item.new_path):
                    lib = bpy.data.libraries.get(item.lib_name)
                    if lib:
                        print(f"Remapping {lib.filepath} → {item.new_path}")
                        lib.filepath = item.new_path
                else:
                    self.report({'WARNING'}, f"New path does not exist: {item.new_path}")
        return {'FINISHED'}

# --- Enregistrement ---
classes = (RemapItem, OT_RemapPaths,)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)