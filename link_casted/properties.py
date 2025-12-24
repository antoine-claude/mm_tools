# properties.py
import bpy
import os
from .core import find_file, match_shot  # Importe tes fonctions utilitaires

def update_scene_properties(scene):
    candidates = find_file(match_shot())

    # Supprime les anciennes propriétés (enlève la propriété de la classe Scene si présente,
    # sinon supprime la propriété personnalisée de l'instance en toute sécurité)
    for prop in list(scene.bl_rna.properties):
        if prop.identifier.startswith("link_"):
            # Remove from bpy.types.Scene if it's a class property we set earlier
            if hasattr(bpy.types.Scene, prop.identifier):
                try:
                    delattr(bpy.types.Scene, prop.identifier)
                except Exception:
                    # Fallback: if it's a custom property on the instance, delete it safely
                    if prop.identifier in scene.keys():
                        del scene[prop.identifier]
            else:
                # If not a class attribute, delete custom property from instance if present
                if prop.identifier in scene.keys():
                    del scene[prop.identifier]

    # Ajoute les nouvelles propriétés
    for path in candidates:
        basename = os.path.basename(path)
        prop_name = f"link_{basename.replace('.', '_')}"
        if not hasattr(scene, prop_name):
            setattr(bpy.types.Scene, prop_name, bpy.props.BoolProperty(name=basename, default=False))
