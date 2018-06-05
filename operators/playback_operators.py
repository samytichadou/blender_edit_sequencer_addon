import bpy

# toggle audio master
class BlenderEditToggleAudioMaster(bpy.types.Operator):
    bl_idname = "blenderedit.toggle_audio_master"
    bl_label = "Toggle Audio Playback"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn=bpy.context.scene
        if scn.use_audio==True:
            scn.use_audio=False
            self.report({'INFO'}, 'Audio UnMuted')
        else:
            scn.use_audio=True
            self.report({'INFO'}, 'Audio Muted')
        return {"FINISHED"}
    
# toggle audio scrubbing
class BlenderEditToggleAudioScrubbing(bpy.types.Operator):
    bl_idname = "blenderedit.toggle_audio_scrubbing"
    bl_label = "Toggle Audio Scrubbing"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scn=bpy.context.scene
        if scn.use_audio_scrub==True:
            scn.use_audio_scrub=False
            self.report({'INFO'}, 'Audio Scrubbing Off')
        else:
            scn.use_audio_scrub=True
            self.report({'INFO'}, 'Audio Scrubbing On')
        return {"FINISHED"}