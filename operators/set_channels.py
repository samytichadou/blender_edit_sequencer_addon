import bpy

from ..misc_functions import create_scene_prop, create_channel_list, create_channel_props

class BlenderEditSetChannels(bpy.types.Operator):
    bl_idname = "blenderedit.set_channels"
    bl_label = "Set Channels"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        create_scene_prop()
        create_channel_list()
        create_channel_props()
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=1000, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        split = layout.split()
        sc_props=bpy.context.scene.blender_edit_scene_properties[0]
        
        col=split.column(align=True)
        for i in range(1,9):
            ch=sc_props.channellist[0].channelprops[i-1]
            row=col.row(align=True)
            row.prop(ch, "name", text=str(i))
            sub = row.row()
            sub.scale_x = 0.1
            sub.prop(ch, "color", text='')
        col=split.column(align=True)
        for i in range(9,17):
            ch=sc_props.channellist[0].channelprops[i-1]
            row=col.row(align=True)
            row.prop(ch, "name", text=str(i))
            sub = row.row()
            sub.scale_x = 0.1
            sub.prop(ch, "color", text='')
        col=split.column(align=True)
        for i in range(17,25):
            ch=sc_props.channellist[0].channelprops[i-1]
            row=col.row(align=True)
            row.prop(ch, "name", text=str(i))
            sub = row.row()
            sub.scale_x = 0.1
            sub.prop(ch, "color", text='')
        col=split.column(align=True)
        for i in range(25,33):
            ch=sc_props.channellist[0].channelprops[i-1]
            row=col.row(align=True)
            row.prop(ch, "name", text=str(i))
            sub = row.row()
            sub.scale_x = 0.1
            sub.prop(ch, "color", text='')
        
    def execute(self, context):
        return {"FINISHED"}