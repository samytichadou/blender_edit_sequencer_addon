import bpy
import os

from ..misc_functions import create_custom_property, clear_custom_property, return_playing_function, return_name_from_strip, create_scene_prop
from ..preferences import get_addon_preferences
from ..json_function import create_clip_json, suppress_existing_file, format_markers_infos, read_json, add_marker_to_json, update_markers_from_temp, update_proxies, format_strip_infos


#load proxys
class BlenderEditLoadProxys(bpy.types.Operator):
    bl_idname = "blenderedit.load_proxys"
    bl_label = "Load Proxys"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    selected=bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        chk=0
        try:
            active=bpy.context.scene.sequence_editor.active_strip
            prefs=get_addon_preferences()
            database=prefs.data_base_folder
            path=os.path.join(database, return_name_from_strip(active).replace('.', '___')+".json")
            data=read_json(path)
            if data['infos']['proxys']!='':
                chk=1
        except:
            chk=0
        return bpy.context.area.type=='SEQUENCE_EDITOR' and chk==1
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'selected')
        layout.prop(self, 'unavailable_path_override', text='Load even if the path does not exist')

    def execute(self, context):
        scn=bpy.context.scene
        prefs=get_addon_preferences()
        database=prefs.data_base_folder
        if self.selected==False:
            active=scn.sequence_editor.active_strip
            json=os.path.join(database, return_name_from_strip(bpy.context.scene.sequence_editor.active_strip).replace('.', '___')+".json")
            datas=read_json(json)
            proxy=datas['infos']['proxys']
            if os.path.isfile(proxy)==True:
                scn.sequence_editor.proxy_storage='PER_STRIP'
                active.use_proxy=True
                active.proxy.use_proxy_custom_directory=False
                active.proxy.use_proxy_custom_file=True
                active.proxy.filepath=proxy
            elif os.path.isdir(proxy)==True:
                scn.sequence_editor.proxy_storage='PER_STRIP'
                active.use_proxy=True
                active.proxy.use_proxy_custom_directory=True
                active.proxy.use_proxy_custom_file=False
                active.proxy.directory=proxy
        else:
            for s in scn.sequence_editor.sequences_all:
                if s.select==True and s.type in {'MOVIE','IMAGE','SOUND'}:
                    json=os.path.join(database, return_name_from_strip(s).replace('.', '___')+".json")
                    datas=read_json(json)
                    proxy=datas['infos']['proxys']
                    if os.path.isfile(proxy)==True:
                        scn.sequence_editor.proxy_storage='PER_STRIP'
                        s.use_proxy=True
                        s.proxy.use_proxy_custom_directory=False
                        s.proxy.use_proxy_custom_file=True
                        s.proxy.filepath=proxy
                    elif os.path.isdir(proxy)==True:
                        scn.sequence_editor.proxy_storage='PER_STRIP'
                        s.use_proxy=True
                        s.proxy.use_proxy_custom_directory=True
                        s.proxy.use_proxy_custom_file=False
                        s.proxy.directory=proxy
                
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {"FINISHED"}