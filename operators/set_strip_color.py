import bpy

from ..misc_functions import get_strip_colors, create_custom_property, clear_custom_property
from ..preferences import get_addon_preferences


class BlenderEditSetStripColor(bpy.types.Operator):
    bl_idname = "blenderedit.set_strip_color"
    bl_label = "Set Strip Color"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    color=bpy.props.IntProperty(min=1, max=12, default=1)
    clear=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        prefs=get_addon_preferences()
        cols=get_strip_colors()
        layout = self.layout
        layout.prop(self, 'clear', text='Clear Strip Colors')
        box=layout.box()
        if self.clear==True:
            box.enabled=False
        box.prop(self, 'color', text='Color')
        col=box.column(align=True)
        for i in range(1,13):
            row=col.row(align=True)
            if self.color!=i:
                row.enabled=False
                row.label(icon='BLANK1')
            else:
                row.label(icon='PLAY')
            prop="scolor"+str(i)
            row.prop(prefs, prop, text='')
            if self.color!=i:
                row.label(icon='BLANK1')
            else:
                row.label(icon='PLAY_REVERSE')

        
    def execute(self, context):
        scn=bpy.context.scene
        for s in scn.sequence_editor.sequences_all:
            if s.select==True:
                if self.clear==True:
                    try:
                        clear_custom_property(s, "blenderedit__color")
                    except KeyError:
                        pass
                else:
                    try:
                        s['blenderedit__color']=self.color
                    except KeyError:
                        create_custom_property(s, "blenderedit__color", self.color)
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        
        return {"FINISHED"}