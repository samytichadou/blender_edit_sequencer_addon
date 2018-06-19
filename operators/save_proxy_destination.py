import bpy
import os

from ..misc_functions import create_custom_property, clear_custom_property, return_playing_function, return_name_from_strip, create_scene_prop
from ..preferences import get_addon_preferences
from ..json_function import create_clip_json, suppress_existing_file, format_markers_infos, read_json, add_marker_to_json, update_markers_from_temp, update_proxies, format_strip_infos


#save load proxys
class BlenderEditSaveProxys(bpy.types.Operator):
    bl_idname = "blenderedit.save_proxys"
    bl_label = "Save Proxys"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    selected=bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None and bpy.context.scene.sequence_editor.active_strip.use_proxy==True and bpy.context.scene.sequence_editor.active_strip.type in {'MOVIE','IMAGE','SOUND'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'selected')

    def execute(self, context):
        scn=bpy.context.scene
        prefs=get_addon_preferences()
        database=prefs.data_base_folder
        if self.selected==False:
            active=scn.sequence_editor.active_strip
            json=os.path.join(database, return_name_from_strip(bpy.context.scene.sequence_editor.active_strip).replace('.', '___')+".json")
            if os.path.isfile(json)==True:
                datas=read_json(json)
                suppress_existing_file(json)
                ndatas=update_proxies(active, datas)
                create_clip_json(json, ndatas)
            else:
                datas=format_strip_infos(active)
                create_clip_json(json, datas)
        else:
            for s in scn.sequence_editor.sequences_all:
                if s.select==True and s.type in {'MOVIE','IMAGE','SOUND'}:
                    json=os.path.join(database, return_name_from_strip(s).replace('.', '___')+".json")
                    if os.path.isfile(json)==True:
                        datas=read_json(json)
                        suppress_existing_file(json)
                        ndatas=update_proxies(s, datas)
                        create_clip_json(json, ndatas)
                    else:
                        datas=format_strip_infos(s)
                        create_clip_json(json, datas)
                
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {"FINISHED"}