import bpy

class BlenderEditSetupUI(bpy.types.Operator):
    bl_idname = "blenderedit.setup_ui"
    bl_label = "Setup UI"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        scn=bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.prop(scn, "blender_edit_ui_glob_offsetX")
        col.prop(scn, "blender_edit_ui_offsetX")
        col.prop(scn, "blender_edit_ui_fontsize")
        col.prop(scn, "blender_edit_ui_channel_fill_alpha")
        col.prop(scn, "blender_edit_ui_channel_fill_alpha_value")
        col.prop(scn, "blender_edit_ui_main_alpha")
        col.prop(scn, "blender_edit_ui_channel_strip_color_onoff")
        col.prop(scn, "blender_edit_ui_strip_color_alpha_value")
        col.prop(scn, "blender_edit_ui_strip_marker_onoff")
        col.prop(scn, "blender_edit_ui_strip_marker_show_hidden")
        col.prop(scn, "blender_edit_ui_strip_marker_color")
        col.prop(scn, "blender_edit_ui_strip_marker_alpha_value")
        col.prop(scn, "blender_edit_ui_marker_name")
        col.prop(scn, "blender_edit_ui_marker_fontsize")
        
    def execute(self, context):
        return {"FINISHED"}