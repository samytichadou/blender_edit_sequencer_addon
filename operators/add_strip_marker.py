import bpy

from ..misc_functions import create_custom_property, clear_custom_property, return_playing_function
from ..preferences import get_addon_preferences

#add strip marker operator
class BlenderEditAddStripMarker(bpy.types.Operator):
    bl_idname = "blenderedit.add_strip_marker"
    bl_label = "Add Strip Marker"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        warn=add_strip_marker_function("comment", False, False)
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
    
    comment=bpy.props.StringProperty(default='comment')
    selected=bpy.props.BoolProperty(default=False)
    all=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'selected', text='Selection Only')
        layout.prop(self, 'all', text='All Playing Clips')
        layout.prop(self, 'comment', text='')
        
    def execute(self, context):
        warn=add_strip_marker_function(self.comment, self.selected, self.all)
        if warn!="":
            self.report({'ERROR'}, warn+"Marker Already Exists")
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        
        return {"FINISHED"}
    
def add_strip_marker_function(comment, selected, all):
    scn=bpy.context.scene
    cf=scn.frame_current
    warn=""
    if selected==True:
        for s in scn.sequence_editor.sequences_all:
            if s.select==True and cf>=s.frame_final_start and cf<=s.frame_final_end:
                try:
                    s["blenderedit__marker_"+str(cf-active.frame_start)]
                    warn+=s.name+' - '
                except KeyError:
                    create_custom_property(s, "blenderedit__marker_"+str(cf-s.frame_start), comment)
    else:
        playing=return_playing_function()
        if all==False:
            active=''
            for s in playing:
                if s.mute==False and active=='':
                    active=s
            if active!='':
                try:
                    active["blenderedit__marker_"+str(cf-active.frame_start)]
                    warn+=active.name+' - '
                except KeyError:
                    create_custom_property(active, "blenderedit__marker_"+str(cf-active.frame_start), comment)
        else:
            for s in playing:
                try:
                    s["blenderedit__marker_"+str(cf-active.frame_start)]
                    warn+=s.name+' - '
                except KeyError:
                    create_custom_property(s, "blenderedit__marker_"+str(cf-s.frame_start), comment)
    return warn