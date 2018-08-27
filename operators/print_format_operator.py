import bpy
import subprocess

from ..preferences import get_addon_preferences
from ..misc_functions import absolute_path

class BlenderEditPrintFFMpegFormats(bpy.types.Operator):
    bl_idname = "blenderedit.print_ffmpeg_formats"
    bl_label = "Print FFmpeg Formats"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        prefs=get_addon_preferences()
        ffmpeg=absolute_path(prefs.ffmpeg_executable)
        #build cmd
        cmd=[ffmpeg,
            "-formats"
            ]
        p=subprocess.Popen(cmd, shell=False)
        return {"FINISHED"}
        