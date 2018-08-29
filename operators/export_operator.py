import bpy
import os
import shutil
import subprocess
import platform

from bpy_extras.io_utils import ExportHelper
from ..preferences import get_addon_preferences
from ..misc_functions import absolute_path
from .multithread.multithread_rendering import multithread_rendering
from .multithread.multithread_functions import create_temp_directories, create_audio_mixdown
        

class BlenderEditExportSequence(bpy.types.Operator, ExportHelper):
    bl_idname = "blenderedit.export_sequence"
    bl_label = "Export Sequence"
    bl_description = ""
    filename_ext = ""
    filepath = bpy.props.StringProperty()
    
    regular=bpy.props.BoolProperty(name='Regular Render', default=False)
    keep_temp=bpy.props.BoolProperty(name='Keep temporary files', default=False)
    free_core=bpy.props.IntProperty(name='Unused Cores', default=2, min=1)
    audio_export=bpy.props.BoolProperty(name='Export Audio Mixdown', default=False)
        
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None and bpy.context.scene.blender_edit_is_rendering==False and bpy.data.is_saved==True
    
    def draw(self, context):
        layout = self.layout
        
        rd = context.scene.render
        image_settings = rd.image_settings
        file_format = image_settings.file_format
        ffmpeg = rd.ffmpeg
        
        layout.prop(self, "regular")
        layout.prop(self, "free_core")
        layout.prop(self, "keep_temp")
        if file_format!='FFMPEG' and self.regular==False:
            layout.prop(self, "audio_export")
        layout.operator("blenderedit.print_ffmpeg_formats")
        
        box=layout.box()
        
        split = box.split()

        col = split.column()
        col.active = not rd.is_movie_format
        col.prop(rd, "use_overwrite")
        col.prop(rd, "use_placeholder")

        col = split.column()
        col.prop(rd, "use_file_extension")
        col.prop(rd, "use_render_cache")
    
        box.template_image_settings(image_settings, color_management=False)
        if rd.use_multiview:
            box.template_image_views(image_settings)

        if file_format == 'QUICKTIME':
            quicktime = rd.quicktime

            split = box.split()
            col = split.column()
            col.prop(quicktime, "codec_type", text="Video Codec")
            col.prop(quicktime, "codec_spatial_quality", text="Quality")

            # Audio
            col.prop(quicktime, "audiocodec_type", text="Audio Codec")
            if quicktime.audiocodec_type != 'No audio':
                split = box.split()
                if quicktime.audiocodec_type == 'LPCM':
                    split.prop(quicktime, "audio_bitdepth", text="")

                split.prop(quicktime, "audio_samplerate", text="")

                split = box.split()
                col = split.column()
                if quicktime.audiocodec_type == 'AAC':
                    col.prop(quicktime, "audio_bitrate")

                subsplit = split.split()
                col = subsplit.column()

                if quicktime.audiocodec_type == 'AAC':
                    col.prop(quicktime, "audio_codec_isvbr")

                col = subsplit.column()
                col.prop(quicktime, "audio_resampling_hq")
                
        if file_format=='FFMPEG':
            box.menu("RENDER_MT_ffmpeg_presets", text="Presets")

            split = box.split()
            split.prop(rd.ffmpeg, "format")
            split.prop(ffmpeg, "use_autosplit")

            box.separator()

            needs_codec = ffmpeg.format in {'AVI', 'QUICKTIME', 'MKV', 'OGG', 'MPEG4'}
            if needs_codec:
                box.prop(ffmpeg, "codec")

            if ffmpeg.codec in {'DNXHD'}:
                box.prop(ffmpeg, "use_lossless_output")

            # Output quality
            if needs_codec and ffmpeg.codec in {'H264', 'MPEG4'}:
                box.prop(ffmpeg, "constant_rate_factor")

            # Encoding speed
            box.prop(ffmpeg, "ffmpeg_preset")
            # I-frames
            box.prop(ffmpeg, "gopsize")
            # B-Frames
            row = box.row()
            row.prop(ffmpeg, "use_max_b_frames", text='Max B-frames')
            pbox = row.split()
            pbox.prop(ffmpeg, "max_b_frames", text='')
            pbox.enabled = ffmpeg.use_max_b_frames

            split = box.split()
            split.enabled = ffmpeg.constant_rate_factor == 'NONE'
            col = split.column()
            col.label(text="Rate:")
            col.prop(ffmpeg, "video_bitrate")
            col.prop(ffmpeg, "minrate", text="Minimum")
            col.prop(ffmpeg, "maxrate", text="Maximum")
            col.prop(ffmpeg, "buffersize", text="Buffer")

            col = split.column()
            col.label(text="Mux:")
            col.prop(ffmpeg, "muxrate", text="Rate")
            col.prop(ffmpeg, "packetsize", text="Packet Size")

            box.separator()

            # Audio:
            if ffmpeg.format != 'MP3':
                box.prop(ffmpeg, "audio_codec", text="Audio Codec")

            row = box.row()
            row.enabled = ffmpeg.audio_codec != 'NONE'
            row.prop(ffmpeg, "audio_bitrate")
            row.prop(ffmpeg, "audio_volume", slider=True)
    
    def execute(self, context):
        bpy.context.scene.blender_edit_is_rendering=True
        if self.regular==True:
            RegularExportSequenceFunction(self.filepath, context)
        else:
            #create temps
            temp_dir, instance_dir, prerender_dir, sound_dir=create_temp_directories(self.filepath)
            
            #audio mixdown
            ffmpeg = bpy.context.scene.render.ffmpeg
            if ffmpeg.audio_codec!='NONE' and bpy.context.scene.render.image_settings.file_format=='FFMPEG' or bpy.context.scene.render.image_settings.file_format!='FFMPEG' and self.audio_export==True:
                create_audio_mixdown(self.filepath, sound_dir)
            
            #save temp for evolution and launch rendering
            clear_temp, lgt, proc=multithread_rendering(self.filepath, self.free_core, self.keep_temp, temp_dir, instance_dir, prerender_dir, sound_dir)
            
            bpy.context.scene.blender_edit_multithread_temp_dir=temp_dir
            bpy.context.scene.blender_edit_multithread_prerender_dir=prerender_dir
            bpy.context.scene.blender_edit_multithread_sound_dir=sound_dir
            bpy.context.scene.blender_edit_multithread_clear_temp=clear_temp
            bpy.context.scene.blender_edit_multithread_lgt=lgt
            bpy.context.scene.blender_edit_multithread_proc=proc
            bpy.context.scene.blender_edit_multithread_audio=self.audio_export
            bpy.types.Scene.blender_edit_multithread_framerate = bpy.context.scene.render.fps
            
            #override context and launch rendering progression check
            for w in bpy.context.window_manager.windows:
                s=w.screen
                for a in s.areas:
                    if a.type == 'SEQUENCE_EDITOR':
                        window=w
                        area=a
                        screen=window.screen
            override = {'window': window, 'screen': screen, 'area': area}
            bpy.ops.blenderedit.check_multithread_rendering(override)

        return {'FINISHED'}

    
### Write Export Function ###
def RegularExportSequenceFunction(filepath, context):
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.opengl(animation=True, sequencer=True)
    return {'FINISHED'}