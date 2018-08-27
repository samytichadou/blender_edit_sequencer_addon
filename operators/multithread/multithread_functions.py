import bpy
import os
import shutil
import signal
import subprocess

from ...preferences import get_addon_preferences
from ...misc_functions import absolute_path

#kill subprocess
def kill_subprocess(processes):
    for p in processes.split('___'):
        if p!='':
            os.kill(int(p), signal.SIGTERM)
            

#create temp dirs
def create_temp_directories(filepath):
    newname=os.path.basename(filepath)
    
    temp_dir=os.path.join(os.path.dirname(filepath), newname+"_temp_render")
    instance_dir=os.path.join(temp_dir,'instances')
    prerender_dir=os.path.join(temp_dir,'prerender')
    sound_dir=os.path.join(temp_dir,'sound')
    
    #create working folder
    if os.path.isdir(temp_dir)==True:
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
    else:
        os.makedirs(temp_dir)
    os.makedirs(instance_dir)
    os.makedirs(prerender_dir)
    os.makedirs(sound_dir)
    
    return (temp_dir, instance_dir, prerender_dir, sound_dir)

#mixdown
def create_audio_mixdown(filepath, sound_dir):
    newname=os.path.basename(filepath)
    temp_name=newname+'_temp_render_sound.wav'
    soundpath=os.path.join(sound_dir, temp_name)
    bpy.ops.sound.mixdown(\
        filepath=soundpath,\
        check_existing=False,\
        relative_path=False,\
        accuracy=1024,\
        container='WAV',\
        codec='PCM',\
        format='S16',\
        bitrate=384,\
        split_channels=False)
        
#concatenate no sound
def concatenate_no_sound(prerender_path, dest_path):
    prefs=get_addon_preferences()
    ffmpeg=absolute_path(prefs.ffmpeg_executable)
    newname=os.path.basename(dest_path)
    temp_name=newname+'_temp_render_##########'
    prerender_pattern=os.path.join(prerender_path, newname+'_temp_render_%10d.')
    
    #build cmd
    cmd=[ffmpeg,
        "-r",
        fps,
        "-i",
        prerender_pattern,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "23",
        "-r",
        fps,
        "-y",
        dest_path
        ]
        
        
        #ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 23 -r 30  -y video-from-frames.mp4
