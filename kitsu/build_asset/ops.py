import shutil

import bpy
import os
from bpy.types import Operator
from .. import cache, prefs
from ..types import (
    Shot,
    Department,
    TaskType
    )


class BUILD_ASSET_OT_build_asset_modeling(Operator):
    """Buld and save the current scene as a asset modeling file"""
    bl_idname = "kitsu.build_asset_modeling"
    bl_label = "Build Asset Modeling"
    bl_description = "Save the current scene with the selected asset name"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        asset_type = cache.asset_type_active_get()
        asset = cache.asset_active_get()
        task_type = cache.task_type_active_get()
        
