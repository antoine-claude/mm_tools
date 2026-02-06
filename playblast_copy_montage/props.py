import bpy


class COPY_OUTPUT_property_group(bpy.types.PropertyGroup):

    copy_output_layer: bpy.props.EnumProperty(
        name="Layer",
        description="Choix du layer de sortie",
        items=[
            ('LAY1', "LAY1", ""),
            ('LAY2', "LAY2", ""),
            ('SPL1_TK1', "SPL1_TK1", ""),
            ('SPL1_TK2', "SPL1_TK2", ""),
            ('SPL2', "SPL2", ""),
            ('SPL3', "SPL3", ""),
        ],
        default='LAY1'
    )

    copy_output_path: bpy.props.StringProperty(
        name="Chemin de destination",
        description="Dossier où copier le fichier .mov",
        subtype='DIR_PATH', 
        default="R:/melodyandmomon/Livraison",
    )


classes = (COPY_OUTPUT_property_group,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.copy_output = bpy.props.PointerProperty(type=COPY_OUTPUT_property_group)

def unregister():
    del bpy.types.Scene.copy_output
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)