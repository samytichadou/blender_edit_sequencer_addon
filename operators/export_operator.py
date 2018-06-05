import bpy

from bpy_extras.io_utils import ExportHelper

class BlenderEditExportSequence(bpy.types.Operator, ExportHelper):
    bl_idname = "blenderedit.export_sequence"
    bl_label = "Export Sequence"
    bl_description = ""
    filename_ext = ""
    filepath = bpy.props.StringProperty()
        
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='SEQUENCE_EDITOR' and bpy.context.scene.sequence_editor is not None
    
    def draw(self, context):
        layout = self.layout
        
        rd = context.scene.render
        image_settings = rd.image_settings
        file_format = image_settings.file_format
        ffmpeg = rd.ffmpeg

        split = layout.split()

        col = split.column()
        col.active = not rd.is_movie_format
        col.prop(rd, "use_overwrite")
        col.prop(rd, "use_placeholder")

        col = split.column()
        col.prop(rd, "use_file_extension")
        col.prop(rd, "use_render_cache")
    
        layout.template_image_settings(image_settings, color_management=False)
        if rd.use_multiview:
            layout.template_image_views(image_settings)

        if file_format == 'QUICKTIME':
            quicktime = rd.quicktime

            split = layout.split()
            col = split.column()
            col.prop(quicktime, "codec_type", text="Video Codec")
            col.prop(quicktime, "codec_spatial_quality", text="Quality")

            # Audio
            col.prop(quicktime, "audiocodec_type", text="Audio Codec")
            if quicktime.audiocodec_type != 'No audio':
                split = layout.split()
                if quicktime.audiocodec_type == 'LPCM':
                    split.prop(quicktime, "audio_bitdepth", text="")

                split.prop(quicktime, "audio_samplerate", text="")

                split = layout.split()
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
            layout.menu("RENDER_MT_ffmpeg_presets", text="Presets")

            split = layout.split()
            split.prop(rd.ffmpeg, "format")
            split.prop(ffmpeg, "use_autosplit")

            layout.separator()

            needs_codec = ffmpeg.format in {'AVI', 'QUICKTIME', 'MKV', 'OGG', 'MPEG4'}
            if needs_codec:
                layout.prop(ffmpeg, "codec")

            if ffmpeg.codec in {'DNXHD'}:
                layout.prop(ffmpeg, "use_lossless_output")

            # Output quality
            if needs_codec and ffmpeg.codec in {'H264', 'MPEG4'}:
                layout.prop(ffmpeg, "constant_rate_factor")

            # Encoding speed
            layout.prop(ffmpeg, "ffmpeg_preset")
            # I-frames
            layout.prop(ffmpeg, "gopsize")
            # B-Frames
            row = layout.row()
            row.prop(ffmpeg, "use_max_b_frames", text='Max B-frames')
            pbox = row.split()
            pbox.prop(ffmpeg, "max_b_frames", text='')
            pbox.enabled = ffmpeg.use_max_b_frames

            split = layout.split()
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

            layout.separator()

            # Audio:
            if ffmpeg.format != 'MP3':
                layout.prop(ffmpeg, "audio_codec", text="Audio Codec")

            row = layout.row()
            row.enabled = ffmpeg.audio_codec != 'NONE'
            row.prop(ffmpeg, "audio_bitrate")
            row.prop(ffmpeg, "audio_volume", slider=True)
    
    def execute(self, context):
        return ExportSequenceFunction(self.filepath, context)
    
    
### Write Export Function ###
def ExportSequenceFunction(filepath, context):
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.opengl(animation=True, sequencer=True)
    return {'FINISHED'} 