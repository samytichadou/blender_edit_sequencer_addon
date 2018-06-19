import bpy
import os

from ..misc_functions import create_custom_property, clear_custom_property, return_playing_function, return_name_from_strip, create_scene_prop
from ..preferences import get_addon_preferences
from ..json_function import create_clip_json, suppress_existing_file, format_markers_infos, read_json, add_marker_to_json, update_markers_from_temp


#modify strip marker menu
class BlenderEditModifyStripMarkerMenu(bpy.types.Operator):
    bl_idname = "blenderedit.modify_strip_marker_menu"
    bl_label = "Modify Strip Marker Menu"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    json=bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        chk=0
        try:
            prefs=get_addon_preferences()
            database=prefs.data_base_folder
            path=os.path.join(database, return_name_from_strip(bpy.context.scene.sequence_editor.active_strip).replace('.', '___')+".json")
            data=read_json(path)
            data['markers'][0]['comment']
            chk=1
        except:
            chk=0
        return chk==1
    
    def invoke(self, context, event):
        wm = context.window_manager
        props=create_scene_prop()
        prefs=get_addon_preferences()
        database=prefs.data_base_folder
        path=self.json=os.path.join(database, return_name_from_strip(bpy.context.scene.sequence_editor.active_strip).replace('.', '___')+".json")
        data=read_json(path)
        for i in range(len(props.tempcomment)-1,-1,-1):
            props.tempcomment.remove(i)
        for m in data['markers']:
            print('new')
            new=props.tempcomment.add()
            new.name=m['comment']
            new.frame=m['frame']
            new.author=m['author']
        
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        props=bpy.context.scene.blender_edit_scene_properties[0]
        layout = self.layout
        col=layout.column(align=True)
        for m in props.tempcomment:
            row=col.row(align=True)
            row.prop(m, 'name', text='')
            row.prop(m, 'frame', text='')
            row.prop(m, 'author', text='author')
            row.prop(m, 'to_clear', text='Clear')
        
    def execute(self, context):
        modify_strip_marker_function(self.json)
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        return {"FINISHED"}
    
def modify_strip_marker_function(json):
    data=update_markers_from_temp(json)
    suppress_existing_file(json)
    create_clip_json(json, data)