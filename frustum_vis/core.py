import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def iter_target_objects(scene):
    """
    Returns:
      - local objects (filtered by rules)
      - objects that instance linked collections (EMPTY with instance_collection)
      - objects inside linked collections (if they are instanced)
    """
    only_mesh = scene.frustum_vis_only_mesh
    limit_col = scene.frustum_vis_collection

    def should_skip(obj):
        for c in obj.users_collection:
            if c.name.startswith("WGT"):
                return True
        if obj.name.endswith("EyesExternal_L_geo") or obj.name.endswith("EyesExternal_R_geo"):
            return True
        return False

    visited = set()

    def scan(col):
        if col in visited:
            return
        visited.add(col)

        # --------------------------------------------------------
        # Case: LINKED COLLECTION → return its instance objects
        # --------------------------------------------------------
        if col.library is not None:
            for obj in scene.objects:
                if obj.instance_collection == col:
                    yield obj
            return

        # --------------------------------------------------------
        # Case: LOCAL COLLECTION → return its objects
        # --------------------------------------------------------
        for obj in col.objects:
            if only_mesh and obj.type != 'MESH':
                continue
            if should_skip(obj):
                continue
            yield obj

        # Recurse into children
        for child in col.children:
            yield from scan(child)

    # If no limit collection specified → return all local objects and linked instances
    if limit_col is None:
        for obj in scene.objects:
            if only_mesh and obj.type != 'MESH':
                continue
            if should_skip(obj):
                continue
            yield obj

        # Also yield all linked collection instances
        for col in bpy.data.collections:
            if col.library is not None:
                for obj in scene.objects:
                    if obj.instance_collection == col:
                        yield obj
        return

    # Otherwise, scan the specified collection and its children
    yield from scan(limit_col)

# --------------------------------------------------------------------
# Main visibility logic
# --------------------------------------------------------------------

def update_visibility_from_camera(scene):
    cam = scene.camera
    if cam is None:
        print("[FrustumVis] No active camera.")
        return

    depsgraph = bpy.context.evaluated_depsgraph_get()
    margin = scene.frustum_vis_margin
    xmin, xmax = -margin, 1.0 + margin
    ymin, ymax = -margin, 1.0 + margin
    visible_count = 0
    hidden_count = 0

    for obj in iter_target_objects(scene):
        obj_eval = obj.evaluated_get(depsgraph)
        visible = False

        # -------------------------------------------------------------
        # Compute visibility for normal objects and for linked instances
        # -------------------------------------------------------------
        if obj_eval.bound_box and obj.type != 'EMPTY':
            bb_world = [
                obj_eval.matrix_world @ Vector(corner)
                for corner in obj_eval.bound_box
            ]
            for co in bb_world:
                ndc = world_to_camera_view(scene, cam, co)
                if ndc.z > 0.0 and xmin <= ndc.x <= xmax and ymin <= ndc.y <= ymax:
                    visible = True
                    break
        else:
            # Use object origin for EMPTY or linked collection instance
            co = obj_eval.matrix_world.translation
            ndc = world_to_camera_view(scene, cam, co)
            visible = (ndc.z > 0.0 and xmin <= ndc.x <= xmax and ymin <= ndc.y <= ymax)

        # -------------------------------------------------------------
        # APPLY VISIBILITY — Works also on linked objects
        # -------------------------------------------------------------
        obj.hide_set(not visible)
        obj.hide_viewport = not visible

        if visible:
            visible_count += 1
        else:
            hidden_count += 1

    print(f"[FrustumVis] Visible: {visible_count}, Hidden: {hidden_count}")
