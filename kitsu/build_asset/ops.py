import bpy
import os
from bpy.types import Operator
from .. import cache, prefs
from ..types import (
    Shot,
    Department,
    TaskType
    )
from .core import *


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
        

class BUILD_ASSETS_OT_build(Operator):
    bl_idname = "kitsu.build_assets"
    bl_label = "Build Assets"
    bl_description = "Save the current scene with the selected shot name"
    bl_options = {'REGISTER'}

    def execute(self, context):
        #Initialize scene for asset
        asset_active = cache.asset_active_get()
        task_type_active = cache.task_type_active_get()
        #check if asset not already build in folder
        asset_dir = prefs.asset_dir_get(context)
        asset_folder_path = os.path.join(asset_dir, asset_active.name, task_type_active.name)
        asset_file_name = f"{asset_active.name}_{task_type_active.short_name}.blend"
        asset_file_path = os.path.join(asset_folder_path, asset_file_name)
        if os.path.exists(asset_file_path):
            self.report({'ERROR'}, f"Asset file already exists: {asset_file_path}")
            return {'CANCELLED'}
        #Create file from general new file
        bpy.ops.wm.read_homefile(app_template="")
        #Clean scene
        for collection in list(bpy.data.collections):
            bpy.data.collections.remove(collection)
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj)
        
        #Create collection
        asset_task_type_collection_name = f"{asset_active.name}_{task_type_active.name}"
        #check if collection already exist in scene
        if not asset_active.name in bpy.data.collections:
            asset_collection = bpy.data.collections.new(asset_active.name)
        else :
            asset_collection = bpy.data.collections[asset_active.name]
        asset_task_type_collection = bpy.data.collections.new(asset_task_type_collection_name)

        bpy.context.scene.collection.children.link(asset_collection)
        asset_collection.children.link(asset_task_type_collection)

        init_modeling_scene_setup(context)
        init_rigging_scene_setup(asset_active)

classes = (
    BUILD_ASSETS_OT_build,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
