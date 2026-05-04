import bpy
import os
import gazu
from dataclasses import asdict, is_dataclass

from ..types import (
    Asset,
    Department,
    )
from .. import cache, bkglobals, prefs
from ..build_shot.core import link_and_override_collection


def get_asset_path(asset_name, asset_dir):

    # parts = asset_name.split('_')
    # asset_type = "FX" if len(parts) > 2 and parts[2].startswith("FX") else (parts[1] if len(parts) > 1 else None)
    asset_type = asset_name.split('_')[1] if len(asset_name.split('_')) > 1 else None

    if asset_type == 'CHR':
        return os.path.join(
            asset_dir, "Characters", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'PRP':
        return os.path.join(
            asset_dir, "Props", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'ITM':
        return os.path.join(
            asset_dir, "SetItems", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    elif asset_type == 'SET':
        return os.path.join(
            asset_dir, "Sets", asset_name, 
            "Final", "Render", f"{asset_name}.blend"
        )
    # elif asset_type == 'FX':
    #     return os.path.join(
    #         asset_dir, "SetItems", asset_name, 
    #         "Final", "Render", f"{asset_name}.blend"
    #     )
    elif asset_name == "MM_Camera":
        return os.path.join(
            asset_dir, "Camera", f"{asset_name}.blend"
        )
    else:
        return None

def asset_path(asset: Asset) -> str:
    #Gather asset path with gazu.files.get_working_files_for_task*
    #Get task for asset 
    asset_active = cache.asset_active_get()
    all_asset_task = asset_active.get_all_tasks()
    task_type_active = cache.task_type_active_get()
    # if asset_active and task_type_active:
    for task in all_asset_task:
        if task.task_type_id == task_type_active.id:
            # print("task_type_name", task.task_type_name, task_type_active.name)
            task_payload = asdict(task) if is_dataclass(task) else task
            # print("task",task_payload)
            working_files = gazu.files.get_working_files_for_task(task_payload)
            if working_files:
                return working_files[0]["path"]
            

def init_modeling_scene_setup():
    """Set up the scene for modeling tasks (e.g., set viewport to solid, set shading to material preview)"""
    asset = cache.asset_active_get()
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
                    space.viewport_shade = 'MATERIAL'
    #Find asset in cache with asset type == Camera and link it to the scene, not MM_Camera just the only asset with asset type = Camera
    #Camera placement : set location to (0,-3,0.5) 
    # bpy.context.scene.cursor.location = (0, -3, 0.5)
    #Link camera
    camera_assets = [a for a in cache.get_all_assets_enum(bpy.context) if 'Camera' in a.name]
    if camera_assets:
        camera_asset = camera_assets[0]
        asset_path = asset_path(camera_asset)
        if asset_path and os.path.exists(asset_path):
            link_and_override_collection(asset_path)
    #
    asset_path = asset_path(asset)
    if asset_path and os.path.exists(asset_path):
        link_and_override_collection(asset_path)


def init_shading_scene_setup(asset) :
    asset_name = asset.name
    task_type_active = cache.task_type_active_get()    

def init_rigging_scene_setup(asset):
    asset_name = asset.name
    task_type_active = cache.task_type_active_get()
    #Copy modeling file to rigging folder, open copy
    asset_dir = prefs.asset_dir_get(bpy.context)
    modeling_path = os.path.join(asset_dir, asset_name, "Modeling", asset_name+"_Modeling"+".blend")
    if modeling_path and os.path.exists(modeling_path):
        rigging_path = os.path.join(asset_dir, asset_name, task_type_active.name, asset_name+"_"+task_type_active.short_name+".blend")
    #append collection with asset name
    with bpy.data.libraries.load(rigging_path, link=False) as (data_from, data_to):
        if asset_name in data_from.collections:
            data_to.collections = [asset_name]
        else:
            print(f"[ERROR] Collection '{asset_name}' not found in {rigging_path}")
            return
    #Create WGTS collection children asset.name col
    asset_col = data_to.collections[0]

    wgts_col = bpy.data.collections.new("WGTS")
    asset_col.children.link(wgts_col)
    wgts_col.hide_viewport = False
    
    rig_col = bpy.data.collections.new(f"{asset_name}_rig")
    asset_col.children.link(rig_col)

    #Add armature object to rig collection
    armature_data = bpy.data.armatures.new(f"{asset_name}_rig")
    armature_obj = bpy.data.objects.new(f"{asset_name}_rig", armature_data)
    rig_col.objects.link(armature_obj)
    #Bone creation
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    pose_bone_data = armature_data.edit_bones.new("pose")
    traj_bone_data = armature_data.edit_bones.new("traj")
    pose_bone_data.head = (0, 0, 0)
    pose_bone_data.tail = (0, 1, 0)
    traj_bone_data.head = (0, 0, 0)
    traj_bone_data.tail = (0, 1, 0)
    traj_bone_data.parent = pose_bone_data
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    pose_bone = armature_obj.pose.bones["pose"]
    traj_bone = armature_obj.pose.bones["traj"]

    #Custom shape cration function 
    def create_circle_with_arrows(name, col, radius=0.1, arrow_length=0.2):
        vertices = [(1.5807852745056152, 0.0, 0.0), (1.280785322189331, -0.39509034156799316, 0.0), (1.280785322189331, -0.19509035348892212, 0.0), (0.9807852506637573, -0.19509035348892212, 0.0), (0.9238795042037964, -0.3826834261417389, 0.0), (0.8314696550369263, -0.5555701851844788, 0.0), (0.7071067690849304, -0.7071067690849304, 0.0), (0.5555717945098877, -0.8314685821533203, 0.0), (0.3826850652694702, -0.9238788485527039, 0.0), (0.19509197771549225, -0.9807849526405334, 0.0), (0.19509197771549225, -1.2807848453521729, 0.0), (0.3950919806957245, -1.2807848453521729, 0.0), (0.0, -1.5807849168777466, 0.0), (-0.3950919806957245, -1.2807848453521729, 0.0), (-0.19509197771549225, -1.2807848453521729, 0.0), (-0.19509197771549225, -0.9807849526405334, 0.0), (-0.3826850652694702, -0.9238788485527039, 0.0), (-0.5555717945098877, -0.8314685821533203, 0.0), (-0.7071067690849304, -0.7071067690849304, 0.0), (-0.8314696550369263, -0.5555701851844788, 0.0), (-0.9238795042037964, -0.3826834261417389, 0.0), (-0.9807852506637573, -0.19509035348892212, 0.0), (-1.280785322189331, -0.19509035348892212, 0.0), (-1.280785322189331, -0.39509034156799316, 0.0), (-1.5807852745056152, 0.0, 0.0), (-1.280785322189331, 0.39509034156799316, 0.0), (-1.280785322189331, 0.19509035348892212, 0.0), (-0.9807852506637573, 0.19509035348892212, 0.0), (-0.9238795042037964, 0.3826834261417389, 0.0), (-0.8314696550369263, 0.5555701851844788, 0.0), (-0.7071067690849304, 0.7071067690849304, 0.0), (-0.5555717945098877, 0.8314685821533203, 0.0), (-0.3826850652694702, 0.9238788485527039, 0.0), (-0.19509197771549225, 0.9807849526405334, 0.0), (-0.19509197771549225, 1.2807848453521729, 0.0), (-0.3950919806957245, 1.2807848453521729, 0.0), (0.0, 1.5807849168777466, 0.0), (0.3950919806957245, 1.2807848453521729, 0.0), (0.19509197771549225, 1.2807848453521729, 0.0), (0.19509197771549225, 0.9807849526405334, 0.0), (0.3826850652694702, 0.9238788485527039, 0.0), (0.5555717945098877, 0.8314685821533203, 0.0), (0.7071067690849304, 0.7071067690849304, 0.0), (0.8314696550369263, 0.5555701851844788, 0.0), (0.9238795042037964, 0.3826834261417389, 0.0), (0.9807852506637573, 0.19509035348892212, 0.0), (1.280785322189331, 0.19509035348892212, 0.0), (1.280785322189331, 0.39509034156799316, 0.0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32), (32, 33), (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 0)]


        mesh = bpy.data.meshes.new(f"WGT_{name}")
        obj = bpy.data.objects.new(f"WGT_{name}", mesh)

        col.objects.link(obj)

        mesh.from_pydata(vertices, edges, [])
        mesh.update()

        return obj

    def create_square(name, col, size=0.6):
        vertices = [(-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]

        mesh = bpy.data.meshes.new(f"WGT_{name}")
        obj = bpy.data.objects.new(f"WGT_{name}", mesh)
        
        col.objects.link(obj)

        mesh.from_pydata(vertices, edges, [])
        mesh.update()

        return obj

    #Add custom shape to traj, circle with arrow on each side 
    pose_custom_shape = create_circle_with_arrows(pose_bone_data.name, wgts_col)
    traj_custom_shape = create_square(traj_bone_data.name, wgts_col)

    pose_bone.custom_shape = pose_custom_shape
    traj_bone.custom_shape = traj_custom_shape

