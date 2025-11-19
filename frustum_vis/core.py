import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def iter_target_objects(scene):
    """Return objects to process, considering mesh-only and collection filter."""
    only_mesh = scene.frustum_vis_only_mesh
    limit_col = scene.frustum_vis_collection

    if limit_col is None:
        for obj in scene.objects:
            if only_mesh and obj.type != 'MESH':
                continue
            yield obj
        return

    visited = set()

    def scan(col):
        if col in visited:
            return
        visited.add(col)

        for obj in col.objects:
            if only_mesh and obj.type != 'MESH':
                continue
            yield obj

        for child in col.children:
            yield from scan(child)

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

        if obj_eval.bound_box:
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
            co = obj_eval.matrix_world.translation
            ndc = world_to_camera_view(scene, cam, co)
            visible = (ndc.z > 0.0 and xmin <= ndc.x <= xmax and ymin <= ndc.y <= ymax)

        obj.hide_set(not visible)
        obj.hide_render = not visible
        obj.hide_viewport = not visible

        if visible:
            visible_count += 1
        else:
            hidden_count += 1

    print(f"[FrustumVis] Visible: {visible_count}, Hidden: {hidden_count}")
