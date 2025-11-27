

# SPDX-FileCopyrightText: 2021 Blender Studio Tools Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later


def preload_modules():
    from . import wheels
    wheels.load_wheels_global_together(
        "openpyxl",
        ["openpyxl", "et_xmlfile"]
    )