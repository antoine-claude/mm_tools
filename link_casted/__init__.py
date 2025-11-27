# link_casted/__init__.py
from .ops import LINKCASTED_OT_link_collection, LINKCASTED_OT_load_files
from .panel_ui import VIEW3D_PT_link_casted
from .core import (match_shot, find_file)

def get_link_casted_classes():
    return (
        VIEW3D_PT_link_casted,
        LINKCASTED_OT_link_collection,
        LINKCASTED_OT_load_files,
    )