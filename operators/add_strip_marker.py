import bpy
import os

from ..misc_functions import create_custom_property, clear_custom_property, return_playing_function, return_name_from_strip
from ..preferences import get_addon_preferences
from ..json_function import create_clip_json, suppress_existing_file, format_markers_infos, read_json, add_marker_to_json

#add strip marker operator
class BlenderEditAddStripMarker(bpy.types.Operator):
    bl_idname = "blenderedit.add_strip_marker"
    bl_label = "Add Strip Marker"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        chk=0
        try:
            chk=return_playing_function()
        except AttributeError:
            pass
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor and chk!=0
    
    def execute(self, context):
        warn=add_strip_marker_function("", False, False, "")
        if warn!="":
            self.report({'ERROR'}, warn+"Marker Already Exists")
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        
        return {"FINISHED"}

#add strip marker menu
class BlenderEditAddStripMarkerMenu(bpy.types.Operator):
    bl_idname = "blenderedit.add_strip_marker_menu"
    bl_label = "Add Strip Marker Menu"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    comment=bpy.props.StringProperty()
    author=bpy.props.StringProperty()
    selected=bpy.props.BoolProperty(default=False)
    all=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        chk=0
        try:
            chk=return_playing_function()
        except AttributeError:
            pass
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor and chk!=0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'selected', text='Selection Only')
        layout.prop(self, 'all', text='All Playing Clips')
        layout.prop(self, 'comment', text='Comment')
        layout.prop(self, 'author', text='Author')
        
    def execute(self, context):
        warn=add_strip_marker_function(self.comment, self.selected, self.all, self.author)
        if warn!="":
            self.report({'ERROR'}, warn+"Marker Already Exists")
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        
        return {"FINISHED"}
    
def add_strip_marker_function(comment, selected, all, author):
    prefs=get_addon_preferences()
    database=prefs.data_base_folder
    scn=bpy.context.scene
    cf=scn.frame_current
    warn=""
    ### custom prop markers
#    if selected==True:
#        for s in scn.sequence_editor.sequences_all:
#            if s.select==True and cf>=s.frame_final_start and cf<=s.frame_final_end:
#                try:
#                    s["blenderedit__marker_"+str(cf-active.frame_start)]
#                    warn+=s.name+' - '
#                except KeyError:
#                    create_custom_property(s, "blenderedit__marker_"+str(cf-s.frame_start), comment)
#    else:
#        playing=return_playing_function()
#        if all==False:
#            active=''
#            for s in playing:
#                if s.mute==False and active=='':
#                    active=s
#            if active!='':
#                try:
#                    active["blenderedit__marker_"+str(cf-active.frame_start)]
#                    warn+=active.name+' - '
#                except KeyError:
#                    create_custom_property(active, "blenderedit__marker_"+str(cf-active.frame_start), comment)
#        else:
#            for s in playing:
#                try:
#                    s["blenderedit__marker_"+str(cf-active.frame_start)]
#                    warn+=s.name+' - '
#                except KeyError:
#                    create_custom_property(s, "blenderedit__marker_"+str(cf-s.frame_start), comment)
    
    ### json markers
    if selected==True:
        for s in scn.sequence_editor.sequences_all:
            if s.select==True and cf>=s.frame_final_start and cf<=s.frame_final_end and s.type in {'MOVIE', 'SOUND', 'IMAGE'}:
                name=return_name_from_strip(s)
                nname=name.replace(".","___")+".json"
                if name!='':
                    if os.path.isfile(os.path.join(database, nname))==False:
                            markerdata=format_markers_infos(s, comment, cf-s.frame_start, author)
                            create_clip_json(os.path.join(database, nname), markerdata)
                    else:
                        chk=0
                        old=read_json(os.path.join(database, nname))
                        for m in old['markers']:
                            if m['frame']==cf-s.frame_start:
                                chk=1
                                warn+=name+' - '
                        if chk==0:
                            suppress_existing_file(os.path.join(database, nname))
                            data=add_marker_to_json(old, comment, cf-s.frame_start, author)
                            create_clip_json(os.path.join(database, nname), data)
    else:
        playing=return_playing_function()
        if all==False:
            active=''
            for s in playing:
                if s.mute==False and active=='' and s.type in {'MOVIE', 'SOUND', 'IMAGE'}:
                    active=s
            if active!='':
                name=return_name_from_strip(active)
                nname=name.replace(".","___")+".json"
                if name!='':
                    if os.path.isfile(os.path.join(database, nname))==False:
                        markerdata=format_markers_infos(s, comment, cf-active.frame_start, author)
                        create_clip_json(os.path.join(database, nname), markerdata)
                    else:
                        chk=0
                        old=read_json(os.path.join(database, nname))
                        for m in old['markers']:
                            if m['frame']==cf-active.frame_start:
                                chk=1
                                warn+=name+' - '
                        if chk==0:
                            suppress_existing_file(os.path.join(database, nname))
                            data=add_marker_to_json(old, comment, cf-active.frame_start, author)
                            create_clip_json(os.path.join(database, nname), data)
        else:
            for s in playing:
                if s.type in {'MOVIE', 'SOUND', 'IMAGE'}:
                    name=return_name_from_strip(s)
                    nname=name.replace(".","___")+".json"
                    if name!='':
                        if os.path.isfile(os.path.join(database, nname))==False:
                            markerdata=format_markers_infos(s, comment, cf-s.frame_start, author)
                            create_clip_json(os.path.join(database, nname), markerdata)
                        else:
                            chk=0
                            old=read_json(os.path.join(database, nname))
                            for m in old['markers']:
                                if m['frame']==cf-s.frame_start:
                                    chk=1
                                    warn+=name+' - '

                            if chk==0:
                                suppress_existing_file(os.path.join(database, nname))
                                data=add_marker_to_json(old, comment, cf-s.frame_start, author)
                                create_clip_json(os.path.join(database, nname), data)
            
    return warn