

# SPDX-FileCopyrightText: 2021 Blender Studio Tools Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

def preload_modules() -> None:
    """Pre-load the datetime module from a wheel so that the API can find it."""
    import sys

    if "openpyxl" in sys.modules:
        return

    from . import wheels

    wheels.load_wheel_global("openpyxl", "openpyxl")
