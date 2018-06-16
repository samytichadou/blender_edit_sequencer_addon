import bpy
import bgl
import blf

from .misc_functions import get_custom_properties, get_strip_colors

class BleditSequencerUI:
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene.sequence_editor is not None
    
    def __init__(self):
        self.handle = bpy.types.SpaceSequenceEditor.draw_handler_add(
                   self.draw_callback_px,(),
                   'WINDOW', 'POST_PIXEL')

    def draw_callback_px(self):
        context=bpy.context
        scn=context.scene
        region = context.region
        cf=bpy.context.scene.frame_current
        
        glob_off_x=scn.blender_edit_ui_glob_offsetX
        off_x=scn.blender_edit_ui_offsetX
        fontsize=scn.blender_edit_ui_fontsize
        fill_alpha=scn.blender_edit_ui_channel_fill_alpha_value
        main_alpha=scn.blender_edit_ui_main_alpha
        strip_color=scn.blender_edit_ui_channel_strip_color_onoff
        strip_color_alpha=scn.blender_edit_ui_strip_color_alpha_value
        marker_color=[*scn.blender_edit_ui_strip_marker_color, scn.blender_edit_ui_strip_marker_alpha_value]

        
        try:
            props=bpy.context.scene.blender_edit_scene_properties[0]
        except IndexError:
            pass
        
        wh=[0.2,0.2,0.2,main_alpha]
        bl=[0.9,0.9,0.9,1]

        xA=20+glob_off_x
        xA2=140+glob_off_x+off_x
        
        font_id = 0
        
        try:
            #strip attributes
            for s in scn.sequence_editor.sequences_all:
                cprops=get_custom_properties(s)
                #colored clips
                if strip_color==True:
                    if 'blenderedit__color' in cprops:
                        for k in cprops:
                            if 'blenderedit__color' in k:
                                try:
                                    val=s[k]
                                    cols=get_strip_colors()
                                    n=int(val)
                                    scol=cols[n-1]
                                except:
                                    break
                                x = s.frame_final_start+0.01
                                y = s.channel+0.2
                                x, y = region.view2d.view_to_region(x, y, clip=False)
                                x2=s.frame_final_end+0.01
                                y2 = s.channel
                                x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
                                w=x2-x
                                h=y2-y
                                #color B
                                bgl.glEnable(bgl.GL_BLEND)
                                bgl.glColor4f(*scol, strip_color_alpha)
                                bgl.glBegin(bgl.GL_QUADS)
                                bgl.glVertex2f(x + w, y + h)
                                bgl.glVertex2f(x, y + h)
                                bgl.glVertex2f(x, y)
                                bgl.glVertex2f(x + w, y)
                                bgl.glEnd()
                                
                #clip markers
                if 'blenderedit__marker' in str(cprops) and scn.blender_edit_ui_strip_marker_onoff==True:
                    for k in cprops:
                        if 'blenderedit__marker' in k:
                            mframe=int(str(k).split("blenderedit__marker_")[1])
                            x=mframe+s.frame_start
                            if scn.blender_edit_ui_strip_marker_show_hidden==True or x>=s.frame_final_start and x<=s.frame_final_end :
                                y = s.channel+0.2
                                x, y = region.view2d.view_to_region(x, y, clip=False)
                                x2 = s.frame_start+mframe+1
                                y2 = s.channel
                                x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
                                x3 = s.frame_start+mframe+0.3
                                x3, y3 = region.view2d.view_to_region(x3, y2, clip=False)
                                bgl.glColor4f(*marker_color)
                                bgl.glLineWidth(4)
                                bgl.glBegin(bgl.GL_QUADS)
                                bgl.glVertex2f(x2, y2)
                                bgl.glVertex2f(x, y2)
                                bgl.glVertex2f(x, y)
                                bgl.glVertex2f(x2, y)
                                bgl.glEnd()
                                bgl.glBegin(bgl.GL_LINE_STRIP)
                                bgl.glVertex2f(x3, y)
                                bgl.glVertex2f(x3, y2)
                                bgl.glEnd()
        except AttributeError:
            pass
                        
        #draw channel numbers
        for n in range(1, 34):
            #vid
            x = context.scene.frame_current-0.5
            y = n
            x, y = region.view2d.view_to_region(x, y, clip=False)
            x2=context.scene.frame_current+0.5
            y2 = n+1
            x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
            x=xA
            x2=xA2
            w=x2-x
            h=y2-y
            
            
            if n!=33:
                #channel fill color
                if scn.blender_edit_ui_channel_fill_alpha==True:
                    try:
                        props.channellist[0].channelprops
                        a=10000
                        #color B
                        col=props.channellist[0].channelprops[n-1].color
                        bgl.glEnable(bgl.GL_BLEND)
                        bgl.glBlendFunc(bgl.GL_DST_COLOR, bgl.GL_ONE)
                        alpha=1-fill_alpha
                        bgl.glColor4f(col[0]-alpha, col[1]-alpha, col[2]-alpha, 0)
                        bgl.glLineWidth(1)
                        bgl.glBegin(bgl.GL_QUADS)
                        bgl.glVertex2f(0, y + h)
                        bgl.glVertex2f(a, y + h)
                        bgl.glVertex2f(a, y)
                        bgl.glVertex2f(0, y)
                        bgl.glEnd()
                    except:
                        pass
                    
                #color B
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
                bgl.glColor4f(*wh)
                bgl.glLineWidth(1)
                bgl.glBegin(bgl.GL_QUADS)
                bgl.glVertex2f(x + w, y + h)
                bgl.glVertex2f(x, y + h)
                bgl.glVertex2f(x, y)
                bgl.glVertex2f(x + w, y)
                bgl.glEnd()
                
                font_id = 0
                bgl.glColor4f(*bl)
                blf.position(font_id, x+5, y+3, 0)
                blf.size(font_id, 13, 72)
                blf.draw(font_id, str(n))
                
                blf.position(font_id, x+20, y+2, 0)
                blf.size(font_id, 13, 72)
                blf.position(font_id, x+35, y+2, 0)
                blf.size(font_id, fontsize, 72)
                try:
                    blf.draw(font_id, str(props.channellist[0].channelprops[n-1].name))
                except :
                    blf.draw(font_id, "Channel "+str(n))
                    
                # horizontal line
                bgl.glColor4f(*bl)
                bgl.glBegin(bgl.GL_LINE_STRIP)
                bgl.glVertex2f(x, y)
                bgl.glVertex2f(x2, y)
                bgl.glEnd()
            else:
                # horizontal line
                bgl.glColor4f(*bl)
                bgl.glBegin(bgl.GL_LINE_STRIP)
                bgl.glVertex2f(x, y)
                bgl.glVertex2f(x2, y)
                bgl.glEnd()
                
        #lines
        y = 1
        x, y = region.view2d.view_to_region(x, y, clip=False)
        x2=context.scene.frame_current+0.5
        y2 = 33
        x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
        x1=xA+27
        x2=xA+17
        x3=xA2
        xoff=glob_off_x+x
        #number separator
        bgl.glColor4f(*bl)
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(x1, y)
        bgl.glVertex2f(x1, y2)
        bgl.glEnd()
        #end line
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(x3, y)
        bgl.glVertex2f(x3, y2)
        bgl.glEnd()
        #start line
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(xA, y)
        bgl.glVertex2f(xA, y2)
        bgl.glEnd()

    def remove_handle(self):
         bpy.types.SpaceSequenceEditor.draw_handler_remove(self.handle, 'WINDOW')