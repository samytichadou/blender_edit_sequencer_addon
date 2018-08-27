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
    "version": (0, 2, 4),
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
from .extra_ui import BleditSequencerUI
from .properties import BlenderEditSceneProperties

# register
##################################

import traceback

widgets = {}

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    widgets["SequencerUI2"] = BleditSequencerUI()
    
    bpy.types.SEQUENCER_HT_header.append(blenderedit_menu_draw)
    
    bpy.types.Scene.blender_edit_scene_properties = \
        bpy.props.CollectionProperty(type=BlenderEditSceneProperties)
        
    bpy.types.Scene.blender_edit_ui_glob_offsetX = bpy.props.IntProperty(name="Global Offset", min=-100)
    bpy.types.Scene.blender_edit_ui_offsetX = bpy.props.IntProperty(name="Offset", min=-100, max=100)
    bpy.types.Scene.blender_edit_ui_fontsize = bpy.props.IntProperty(name="Font Size", default=12, min=1, max=30)
    bpy.types.Scene.blender_edit_ui_channel_fill_alpha = bpy.props.BoolProperty(name="Channel Fill Toggle", default=True)
    bpy.types.Scene.blender_edit_ui_channel_fill_alpha_value = bpy.props.FloatProperty(name="Channel Fill Value", default=0.5, min=0, max=1)
    bpy.types.Scene.blender_edit_ui_main_alpha = bpy.props.FloatProperty(name="Main UI Background", default=0.9, min=0, max=1)
    bpy.types.Scene.blender_edit_ui_channel_strip_color_onoff = bpy.props.BoolProperty(name="Strip Color Toggle", default=True)
    bpy.types.Scene.blender_edit_ui_strip_color_alpha_value = bpy.props.FloatProperty(name="Strip Color Alpha Value", default=1, min=0, max=1)
    bpy.types.Scene.blender_edit_ui_strip_marker_onoff = bpy.props.BoolProperty(name="Show Strip Markers", default=True)
    bpy.types.Scene.blender_edit_ui_strip_marker_show_hidden = bpy.props.BoolProperty(name="Show Hidden Strip Markers", default=False)
    bpy.types.Scene.blender_edit_ui_strip_marker_alpha_value = bpy.props.FloatProperty(name="Markers Alpha Value", default=1, min=0, max=1)
    bpy.types.Scene.blender_edit_ui_strip_marker_color = bpy.props.FloatVectorProperty(name="Markers Color", min=0.0, max=1.0, default=[1, 1, 1], subtype='COLOR')
    bpy.types.Scene.blender_edit_ui_marker_name = bpy.props.BoolProperty(name="Show Markers Name", default=True)
    bpy.types.Scene.blender_edit_ui_marker_fontsize = bpy.props.IntProperty(name="Font Size", default=12, min=1, max=30)
    bpy.types.Scene.blender_edit_ui_ismarker = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.blender_edit_multithread_temp_dir = bpy.props.StringProperty()
    bpy.types.Scene.blender_edit_multithread_prerender_dir = bpy.props.StringProperty()
    bpy.types.Scene.blender_edit_multithread_sound_dir = bpy.props.StringProperty()
    bpy.types.Scene.blender_edit_multithread_clear_temp = bpy.props.BoolProperty()
    bpy.types.Scene.blender_edit_multithread_lgt = bpy.props.IntProperty()
    bpy.types.Scene.blender_edit_is_rendering = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.blender_edit_multithread_is_ffmpeg = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.blender_edit_multithread_proc = bpy.props.StringProperty()
    bpy.types.Scene.blender_edit_multithread_audio = bpy.props.BoolProperty()
    bpy.types.Scene.blender_edit_multithread_framerate = bpy.props.IntProperty()
    
def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
    
    bpy.types.SEQUENCER_HT_header.remove(blenderedit_menu_draw)
    
    for key, dc in widgets.items():
        dc.remove_handle()
        
    del bpy.types.Scene.blender_edit_scene_properties
    del bpy.types.Scene.blender_edit_ui_glob_offsetX
    del bpy.types.Scene.blender_edit_ui_offsetX
    del bpy.types.Scene.blender_edit_ui_fontsize
    del bpy.types.Scene.blender_edit_ui_channel_fill_alpha
    del bpy.types.Scene.blender_edit_ui_channel_fill_alpha_value
    del bpy.types.Scene.blender_edit_ui_main_alpha
    del bpy.types.Scene.blender_edit_ui_channel_strip_color_onoff
    del bpy.types.Scene.blender_edit_ui_strip_color_alpha_value
    del bpy.types.Scene.blender_edit_ui_strip_marker_onoff
    del bpy.types.Scene.blender_edit_ui_strip_marker_show_hidden
    del bpy.types.Scene.blender_edit_ui_strip_marker_color
    del bpy.types.Scene.blender_edit_ui_marker_name
    del bpy.types.Scene.blender_edit_ui_marker_fontsize
    del bpy.types.Scene.blender_edit_ui_ismarker
    del bpy.types.Scene.blender_edit_multithread_temp_dir
    del bpy.types.Scene.blender_edit_multithread_prerender_dir
    del bpy.types.Scene.blender_edit_multithread_sound_dir
    del bpy.types.Scene.blender_edit_multithread_clear_temp
    del bpy.types.Scene.blender_edit_multithread_lgt
    del bpy.types.Scene.blender_edit_is_rendering
    del bpy.types.Scene.blender_edit_multithread_is_ffmpeg
    del bpy.types.Scene.blender_edit_multithread_proc
    del bpy.types.Scene.blender_edit_multithread_audio
    del bpy.types.Scene.blender_edit_multithread_framerate