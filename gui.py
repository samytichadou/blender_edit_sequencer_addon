import bpy

class BlenderEditFooterMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_footer_menu"
    bl_label = "Blender Edit Menu"

    def draw(self, context):
        layout = self.layout
        layout.menu('view3d.blender_edit_settings_menu', text='Settings')
        layout.menu('view3d.blender_edit_strips_menu', text='Strips')
        layout.menu('view3d.blender_edit_timeline_menu', text='Timeline')
        layout.menu('view3d.blender_edit_playback_menu', text='Playback')
        layout.menu('view3d.blender_edit_misc_menu', text='Misc')
        
class BlenderEditSettingsMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_settings_menu"
    bl_label = "Blender Settings Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("blenderedit.set_scene_format")
        layout.operator("blenderedit.export_sequence")
        layout.operator("blenderedit.set_channels")
        layout.operator("blenderedit.setup_ui")
        
class BlenderEditStripsMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_strips_menu"
    bl_label = "Blender Strips Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("blenderedit.set_strip_color")
        layout.operator("blenderedit.select_by_color")
        layout.operator("blenderedit.add_strip_marker_menu")
        
class BlenderEditTimelineMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_timeline_menu"
    bl_label = "Blender Edit Timeline Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("blenderedit.set_start")
        layout.operator("blenderedit.set_end")
        layout.separator()
        ffw=layout.operator("blenderedit.move_clips", text='Move Clips 1 frame forward')
        ffw.forward=True
        ffw.ten_frames=False
        ffw.vertical=False
        tfw=layout.operator("blenderedit.move_clips", text='Move Clips 10 frame forward')
        tfw.forward=True
        tfw.ten_frames=True
        tfw.vertical=False
        fbw=layout.operator("blenderedit.move_clips", text='Move Clips 1 frame backward')
        fbw.forward=False
        fbw.ten_frames=False
        fbw.vertical=False
        tbw=layout.operator("blenderedit.move_clips", text='Move Clips 10 frame backward')
        tbw.forward=False
        tbw.ten_frames=True
        tbw.vertical=False
        layout.separator()
        ufw=layout.operator("blenderedit.move_clips", text='Move Clips Up')
        ufw.forward=True
        ufw.ten_frames=False
        ufw.vertical=True
        dfw=layout.operator("blenderedit.move_clips", text='Move Clips Down')
        dfw.forward=False
        dfw.ten_frames=False
        dfw.vertical=True
        layout.separator()
        layout.operator("blenderedit.select_channel_menu")
        layout.separator()
        layout.operator("blenderedit.select_handles_menu")
        layout.operator("blenderedit.select_playing_menu")
        layout.operator("blenderedit.select_left_right_menu")
        layout.separator()
        layout.operator("blenderedit.cut_all_menu")
        layout.separator()
        layout.operator("blenderedit.go_to_in_out_menu")
        
class BlenderEditPlaybackMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_playback_menu"
    bl_label = "Blender Edit Playback Menu"

    def draw(self, context):
        scn=bpy.context.scene
        screen=bpy.context.screen
        layout = self.layout
        layout.prop(scn, "use_audio")
        layout.prop(scn, "use_audio_sync")
        layout.prop(scn, "use_audio_scrub")
        layout.separator()
        layout.prop(scn, "use_frame_drop")
        layout.separator()
        layout.prop(screen, "use_follow")
        
class BlenderEditMiscMenu(bpy.types.Menu):
    bl_idname = "view3d.blender_edit_misc_menu"
    bl_label = "Blender Edit Misc Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.search_menu")
        layout.operator("sequencer.offset_clear")
        
def blenderedit_menu_draw(self, context):
    layout = self.layout
    layout.menu('view3d.blender_edit_footer_menu', text='Settings')