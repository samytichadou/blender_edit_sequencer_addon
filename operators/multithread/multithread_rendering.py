import bpy
import os
import multiprocessing
import subprocess
import shutil
import shlex

from ...preferences import get_addon_preferences

def multithread_rendering(filepath, free_core, keep_temp, temp_dir, instance_dir, prerender_dir, sound_dir):
    scn=bpy.context.scene
    
    processes=''
    
    blender=bpy.app.binary_path
    
    newname=os.path.basename(filepath)
    
    core_number=multiprocessing.cpu_count()-free_core
    
    #get number of frame to render
    lgt=scn.frame_end-scn.frame_start
    st=scn.frame_start
    en=scn.frame_end
        
    #get frame per core
    flt_fr_per_core=lgt/core_number
    int_fr_per_core=int(flt_fr_per_core)
    extra_fr=lgt-(int_fr_per_core*core_number)
        
    #save main file
    o_blend=bpy.data.filepath
    bpy.ops.wm.save_as_mainfile(filepath=o_blend)
    
    #save instances
    for i in range(1, core_number+1):
        temp_name=newname+'_temp_render_'+str(i).zfill(10)
        scn.render.filepath=os.path.join(prerender_dir, temp_name)
        
        nstart=st+(i-1)*int_fr_per_core
        nend=st+(i)*int_fr_per_core

        scn.frame_start=nstart
        scn.frame_end=nend
        
        #get the extra_fr in the last instance
        if i==core_number and extra_fr!=0:
            scn.frame_end=en
        
        if scn.render.image_settings.file_format=='FFMPEG':
            scn.render.image_settings.file_format='PNG'
            scn.render.image_settings.compression=0
            scn.render.image_settings.color_depth = '16'
            
            scn.blender_edit_multithread_is_ffmpeg=True
        else:
            scn.blender_edit_multithread_is_ffmpeg=False

        
        blend_name=temp_name+'.blend'
        blend_path=os.path.join(instance_dir, blend_name)
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        
        #build cmd
        cmd=[blender,
            "-b",
            blend_path,
            "-a"
            ]
        #cmd='"'+blender+'"'+" -b "+'"'+blend_path+'"'+" -a"
        p=subprocess.Popen(cmd, shell=False)
        processes+=str(p.pid)+"___"
        
    bpy.ops.wm.open_mainfile(filepath=o_blend)
    
    if keep_temp==1:
        clear_temp=0
    else:
        clear_temp=1
    
    return(clear_temp, lgt, processes)