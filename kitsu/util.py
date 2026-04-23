# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
#
# (c) 2021, Blender Foundation - Paul Golter

import re
from typing import Union

import bpy
import os
from . import bkglobals


def ui_redraw() -> None:
    """
    Forces blender to redraw the UI.
    """
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()


def get_version(str_value: str, format: type = str) -> Union[str, int, None]:
    match = re.search(bkglobals.VERSION_PATTERN, str_value)
    if match:
        version = match.group()
        if format == str:
            return version
        if format == int:
            return int(version.replace("v", ""))
    return None


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
