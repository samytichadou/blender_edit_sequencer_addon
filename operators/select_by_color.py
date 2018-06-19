import bpy

from ..misc_functions import get_strip_colors, create_custom_property, clear_custom_property
from ..preferences import get_addon_preferences


class BlenderEditSelectByColor(bpy.types.Operator):
    bl_idname = "blenderedit.select_by_color"
    bl_label = "Select Strip By Color"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    color=bpy.props.IntProperty(min=1, max=12, default=1)
    add=bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        prefs=get_addon_preferences()
        cols=get_strip_colors()
        layout = self.layout
        layout.prop(self, 'color', text='Color')
        layout.prop(self, 'add', text='Add to Selection')
        col=layout.column(align=True)
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
        if self.add==False:
            for s in scn.sequence_editor.sequences_all:
                s.select=False
        for s in scn.sequence_editor.sequences_all:
            try:
                if s['blenderedit__color']==self.color:
                    s.select=True
            except KeyError:
                pass
        for a in bpy.context.screen.areas:
            a.tag_redraw()
        
        return {"FINISHED"}