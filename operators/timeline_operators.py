import bpy
import os

from operator import itemgetter

from ..misc_functions import return_playing_function, return_name_from_strip
from ..preferences import get_addon_preferences
from ..json_function import read_json

# set in point
class BlenderEditSetStart(bpy.types.Operator):
    bl_idname = "blenderedit.set_start_end"
    bl_label = "Set Start-End"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    end=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scn=bpy.context.scene
        if bpy.context.scene.use_preview_range == False:
            if self.end==False:
                scn.frame_start = scn.frame_current
            else:
                scn.frame_end = scn.frame_current-1
        else:
            if self.end==False:
                scn.frame_preview_start = scn.frame_current
            else:
                scn.frame_preview_end = scn.frame_current-1
        return {"FINISHED"}
    
# move selected
class BlenderEditMoveClips(bpy.types.Operator):
    bl_idname = "blenderedit.move_clips"
    bl_label = "Move Clips"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    forward=bpy.props.BoolProperty()
    ten_frames=bpy.props.BoolProperty()
    vertical=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        if self.vertical==True:
            if self.forward==True:
                bpy.ops.transform.seq_slide(value=(0, 1)) 
            else:
                bpy.ops.transform.seq_slide(value=(0, -1)) 
        else:
            if self.forward==True and self.ten_frames==False:
                bpy.ops.transform.seq_slide(value=(1, 0))    
            elif self.forward==True and self.ten_frames==True:
                bpy.ops.transform.seq_slide(value=(10, 0))
            elif self.forward==False and self.ten_frames==False:
                bpy.ops.transform.seq_slide(value=(-1, 0))
            elif self.forward==False and self.ten_frames==True:
                bpy.ops.transform.seq_slide(value=(-10, 0))

        return {"FINISHED"}
    
# select by channel
class BlenderEditSelectChannel(bpy.types.Operator):
    bl_idname = "blenderedit.select_channel"
    bl_label = "Select Channel"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    add=bpy.props.BoolProperty()
    channel=bpy.props.IntProperty(min=1, max=32)

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def execute(self, context):
        SelectByChannel(self.add, self.channel)
        return {"FINISHED"}
    
# select by channel menu
class BlenderEditSelectChannelMenu(bpy.types.Operator):
    bl_idname = "blenderedit.select_channel_menu"
    bl_label = "Select Channel"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    add=bpy.props.BoolProperty()
    channel=bpy.props.IntProperty(min=1, max=32)

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'add')
        layout.prop(self, 'channel')

    def execute(self, context):
        SelectByChannel(self.add, self.channel)
        return {"FINISHED"}
    
# select by channel function
def SelectByChannel(add, channel):
    scn=bpy.context.scene
    channelstrip=[]
    chk=0
    for s in scn.sequence_editor.sequences_all:
        if add==False:
            s.select=False
            s.select_left_handle=False
            s.select_right_handle=False
        if s.channel==channel:
            if add==False:
                s.select=True
            else:
                channelstrip.append(s)
                if s.select==True:
                    chk=1
    if add==True:
        if chk==0:
            for s in channelstrip:
                s.select=True
        else:
            for s in channelstrip:
                s.select=False
                s.select_left_handle=False
                s.select_right_handle=False
    return {"FINISHED"}

# select handles
class BlenderEditSelectHandles(bpy.types.Operator):
    bl_idname = "blenderedit.select_handles"
    bl_label = "Select Handles"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    right=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        if self.right==True:
            bpy.ops.sequencer.strip_jump(next=True, center=False)
        else:
            bpy.ops.sequencer.strip_jump(next=False, center=False)
        SelectHandlesFunction(self.right)
        return {"FINISHED"}
    
# select handles function
def SelectHandlesFunction(right):
    scn=bpy.context.scene
    cf=scn.frame_current
    r_select=[]
    l_select=[]
    channel=[]
    trimlist=[]
    active=0
    for s in scn.sequence_editor.sequences_all:
        s.select=False
        s.select_left_handle=False
        s.select_right_handle=False
        if s.frame_final_start==cf:
            l_select.append(s)
        if s.frame_final_end==cf:
            r_select.append(s)
    for s in r_select:
        s.select=s.select_right_handle=True
    for s in l_select:
        s.select=s.select_left_handle=True
    
    return {"FINISHED"}

# select playing
class BlenderEditSelectPlaying(bpy.types.Operator):
    bl_idname = "blenderedit.select_playing"
    bl_label = "Select Playing Clips"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    all=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        SelectPlayingFunction(self.all)
        return {"FINISHED"}
    
# select playing Menu
class BlenderEditSelectPlayingMenu(bpy.types.Operator):
    bl_idname = "blenderedit.select_playing_menu"
    bl_label = "Select Playing Clips Menu"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    all=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'all')

    def execute(self, context):
        SelectPlayingFunction(self.all)
        return {"FINISHED"}
    
# select active function
def SelectPlayingFunction(all):
    scn=bpy.context.scene
    cf=scn.frame_current
    active=''
    for s in scn.sequence_editor.sequences_all:
        s.select=False
        s.select_left_handle=False
        s.select_right_handle=False
    playing=return_playing_function()
    if len(playing)!=0:
        for s in playing:
            if s.mute==False and active=='':
                active=s
            if all==True:
                s.select=True
            else:
                if active!='':
                    active.select=True
        if active!='':
            scn.sequence_editor.active_strip=active
    return {"FINISHED"}

# cut all
class BlenderEditCutAll(bpy.types.Operator):
    bl_idname = "blenderedit.cut_all"
    bl_label = "Cut All Playing Clip"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    all=bpy.props.BoolProperty()
    hard=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        CutAllFunction(self.all, self.hard)
        return {"FINISHED"}
    
# cut all menu
class BlenderEditCutAllMenu(bpy.types.Operator):
    bl_idname = "blenderedit.cut_all_menu"
    bl_label = "Cut All Playing Clip Menu"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    all=bpy.props.BoolProperty()
    hard=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'all')
        layout.prop(self, 'hard')

    def execute(self, context):
        CutAllFunction(self.all, self.hard)
        return {"FINISHED"}
    
# cut all function
def CutAllFunction(all, hard):
    scn=bpy.context.scene
    cf=scn.frame_current
    playing=[]
    channel=[]
    active=0
    for s in scn.sequence_editor.sequences_all:
        s.select=False
        s.select_left_handle=False
        s.select_right_handle=False
        if s.frame_final_start<=cf and s.frame_final_end > cf:
            if all==True:
                playing.append(s)
                channel.append(s.channel)
            else:
                if s.mute==False:
                    playing.append(s)
                    channel.append(s.channel)
    if len(playing)!=0:
        for s in playing:
            maximum=max(channel)
            if s.channel==maximum:
                active=s
            if all==True:
                s.select=True
            else:
                if active!=0:
                    active.select=True
        if hard==False:
            bpy.ops.sequencer.cut(frame=scn.frame_current, type='HARD')
        else:
            bpy.ops.sequencer.cut(frame=scn.frame_current, type='SOFT')
        for s in scn.sequence_editor.sequences_all:
            s.select=False
                        
    return {"FINISHED"}

# select left right
class BlenderEditSelectLeftRight(bpy.types.Operator):
    bl_idname = "blenderedit.select_left_right"
    bl_label = "Select Left Right"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    right=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        SelectLeftRightFunction(self.right)
        return {"FINISHED"}
    
# select left right function
def SelectLeftRightFunction(right):
    scn=bpy.context.scene
    cf=scn.frame_current
    playing=[]
    channel=[]
    active=0
    for s in scn.sequence_editor.sequences_all:
        s.select=False
        s.select_left_handle=False
        s.select_right_handle=False
        if right==True:
            if s.frame_final_end>cf :
                s.select=True
        else:
            if s.frame_final_start<cf :
                s.select=True
                        
    return {"FINISHED"}

# go to in out
class BlenderEditGoToInOut(bpy.types.Operator):
    bl_idname = "blenderedit.go_to_in_out"
    bl_label = "Go to Strip In Out"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    out=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        GoToInOutFunction(self.out)
        return {"FINISHED"}
    
    
# go to in out function
def GoToInOutFunction(out):
    scn=bpy.context.scene
    cf=scn.frame_current
    selected=[]
    for s in scn.sequence_editor.sequences_all:
        if s.select==True:
            selected.append([s.frame_final_start, s.frame_final_end])
    if len(selected)!=0:
        if out==False:
            scn.frame_current=min(selected,key=itemgetter(0))[0]
        else:
            scn.frame_current=max(selected,key=itemgetter(1))[1]
                                
    return {"FINISHED"}

# jump to next marker
class BlenderEditGoToMarkers(bpy.types.Operator):
    bl_idname = "blenderedit.go_to_markers"
    bl_label = "Go to Markers"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    next=bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None

    def execute(self, context):
        prefs=get_addon_preferences()
        database=prefs.data_base_folder
        scn=bpy.context.scene
        hidden=scn.blender_edit_ui_strip_marker_show_hidden
        cf=scn.frame_current
        list=[]
        for s in scn.sequence_editor.sequences_all:
            name=return_name_from_strip(s)
            path=os.path.join(database, name.replace('.', '___')+".json")
            if os.path.isfile(path)==True:
                data=read_json(path)
                for m in data['markers']:
                    fr=m['frame']+s.frame_start
                    if self.next==False and fr<cf:
                        if hidden==True:
                            list.append(fr)
                        elif hidden==False and fr>=s.frame_final_start and fr<=s.frame_final_end:
                            list.append(fr)
                    elif self.next==True and m['frame']+s.frame_start>cf:
                        if hidden==True:
                            list.append(fr)
                        elif hidden==False and fr>=s.frame_final_start and fr<=s.frame_final_end:
                            list.append(fr)
        if len(list)!=0 and self.next==True:
            list=sorted(list)
            scn.frame_current=list[0]
        elif len(list)!=0 and self.next==False:
            list=sorted(list, reverse=True)
            scn.frame_current=list[0]
        else:
            self.report({'INFO'}, "No More Strip Markers in this Direction")
        
        return {"FINISHED"}