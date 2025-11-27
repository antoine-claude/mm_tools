# properties.py
import bpy
import os
from .core import find_file, match_shot  # Importe tes fonctions utilitaires

def update_scene_properties(scene):
    candidates = find_file(match_shot())

    # Supprime les anciennes propriétés
    for prop in scene.bl_rna.properties:
        if prop.identifier.startswith("link_"):
            del scene[prop.identifier]

    # Ajoute les nouvelles propriétés
    for path in candidates:
        basename = os.path.basename(path)
        prop_name = f"link_{basename.replace('.', '_')}"
        if not hasattr(scene, prop_name):
            setattr(bpy.types.Scene, prop_name, bpy.props.BoolProperty(name=basename, default=False))
