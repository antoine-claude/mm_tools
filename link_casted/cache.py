import bpy

# Simple module-level cache for precomputed link properties/groups
CACHE = {
    "has_props": False,
    "others": [],
    "groups": {"CHR": [], "PRP": [], "SET": [], "CAMERA": []},
}


def update_cache(scene: bpy.types.Scene):
    """Scan the scene for dynamic `link_` properties and populate CACHE.
    This is intended to be called from the load operator so the UI draw
    doesn't have to perform heavy computation.
    """
    link_props = [p for p in dir(scene) if p.startswith("link_")]

    groups = {"CHR": [], "PRP": [], "SET": [], "CAMERA": []}
    others = []

    for prop in link_props:
        parts = prop.split("_")
        if len(parts) > 2:
            key = parts[2].upper()
            prefix = (key[:6] if key == "CAMERA" else key[:3])
            if prefix in groups:
                groups[prefix].append(prop)
            else:
                others.append(prop)
        else:
            others.append(prop)

    for k in groups:
        groups[k].sort()
    others.sort()

    CACHE["has_props"] = bool(link_props)
    CACHE["others"] = others
    CACHE["groups"] = groups


def get_cached():
    return CACHE
