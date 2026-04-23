# SPDX-FileCopyrightText: 2021 Blender Studio Tools Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

filetree_default = {
    "working": {
        "mountpoint": "R:",
        "root": "",
        "folder_path": {
            "shot": "<Project>/shots/production/<Episode>/<Sequence>/<Shot>/<TaskType>/work",
            "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/work",
            "sequence": "<Project>/shots/production/<Episode>/<Sequence>/<TaskType>/work",
            "style": "lowercase",
        },
        "file_name": {
            "shot": "<Episode>_<Sequence>_<Shot>_<TaskType>_work",
            "asset": "<Asset>_<TaskType>_work",
            "sequence": "<Episode>_<Sequence>_<TaskType>_work",
            "style": "lowercase",
        },
    },
    "output": {
        "mountpoint": "",
        "root": "",
        "folder_path": {
            "shot": "<Project>/shots/production/<Episode>/<Sequence>/<Shot>/<TaskType>/publish",
            "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/publish",
            "sequence": "<Project>/shots/production/<Episode>/<Sequence>/<TaskType>/publish",
            "style": "lowercase",
        },
        "file_name": {
            "shot": "<Episode>_<Sequence>_<Shot>_<TaskType>_publish",
            "asset": "<Asset>_<TaskType>_publish",
            "sequence": "<Episode>_<Sequence>_<TaskType>_publish",
            "style": "lowercase",
        },
    },
    "preview": {
        "mountpoint": "",
        "root": "",
        "folder_path": {
            "shot": "<Project>/shots/production/<Sequence>/<Shot>/<TaskType>/preview",
            "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/preview",
            "sequence": "<Project>/shots/production/<Sequence>/<TaskType>/preview",
            "style": "lowercase",
        },
        "file_name": {
            "shot": "<Shot>_<TaskType>_preview",
            "asset": "<Asset>_<TaskType>_preview",
            "sequence": "<Sequence>_<TaskType>_preview",
            "style": "lowercase",
        },
    },
}
