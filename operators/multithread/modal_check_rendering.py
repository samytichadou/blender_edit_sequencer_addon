import bpy
import os
import shutil
import time

from .multithread_functions import kill_subprocess

class BlenderEditCheckMultithreadRendering(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "blenderedit.check_multithread_rendering"
    bl_label = "Check Multithread Rendering"

    _timer = None

    def modal(self, context, event):
        prerender_dir = bpy.context.scene.blender_edit_multithread_prerender_dir
    
        frame_to_render = bpy.context.scene.blender_edit_multithread_lgt+1
        
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            lgt=len([name for name in os.listdir(prerender_dir) if os.path.isfile(os.path.join(prerender_dir, name))])
            if lgt==frame_to_render:
                self.finish(context)
                return {'FINISHED'}
            else:
                coef=40/frame_to_render
                prog=int(lgt*coef)
                prog_bar="[ "+"|"*prog+"-"*(40-prog)+" ]"
                nb=str(lgt)+"/"+str(frame_to_render)
    
                self.report({'INFO'}, "Rendering : "+prog_bar+" "+nb)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.3, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        proc= bpy.context.scene.blender_edit_multithread_proc
        self.report({'INFO'}, "Render Canceled")
        
        #kill render process
        kill_subprocess(proc)
        
        #launch cleaning if needed
        if bpy.context.scene.blender_edit_multithread_clear_temp==True:
            time.sleep(1)
            try:
                shutil.rmtree(bpy.context.scene.blender_edit_multithread_temp_dir)
            except:
                self.report({'WARNING'}, "Error Cleaning Temps")
        
        #temp
        bpy.context.scene.blender_edit_is_rendering=False
        
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def finish(self, context):
        self.report({'INFO'}, "Render Finished")
        
        #launch concatenation if needed
        #if bpy.context.scene.blender_edit_multithread_is_ffmpeg==True:
                        
        #check for it
        bpy.ops.blenderedit.post_rendering_actions_check()
        
        #temp
        bpy.context.scene.blender_edit_is_rendering=False