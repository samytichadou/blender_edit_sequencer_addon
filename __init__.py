'''
Copyright (C) 2018 Samy Tichadou (tonton)
YOUR@MAIL.com

Created by Samy Tichadou (tonton)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Blender Edit 2 alpha",
    "description": "",
    "author": "Samy Tichadou (tonton)",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "Sequencer",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Sequencer" }


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

from .gui import blenderedit_menu_draw

# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    bpy.types.SEQUENCER_HT_header.append(blenderedit_menu_draw)

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
    
    bpy.types.SEQUENCER_HT_header.remove(blenderedit_menu_draw)
