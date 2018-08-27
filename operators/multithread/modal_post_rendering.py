import bpy
import os

class BlenderEditPostRenderingActionsCheck(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "blenderedit.post_rendering_actions_check"
    bl_label = "Post Rendering Actions Check"

    _timer = None
    
#    def __init__(self):
#        bpy.types.Scene.blender_edit_is_rendering=False

    def modal(self, context, event):
        prerender_dir = bpy.context.scene.blender_edit_multithread_prerender_dir
    
        frame_to_render = bpy.context.scene.blender_edit_multithread_lgt+1
        
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.finish(context)
            return {'FINISHED'}
            self.report({'INFO'}, str(lgt)+"/"+str(frame_to_render))
            print(str(lgt)+"/"+str(frame_to_render))

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.3, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self.report({'INFO'}, "Render Canceled")
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def finish(self, context):
        self.report({'INFO'}, "Render Finished")