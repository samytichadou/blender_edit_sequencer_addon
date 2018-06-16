import bpy

from .preferences import get_addon_preferences

#create scene prop
def create_scene_prop():
    try:
        bpy.context.scene.blender_edit_scene_properties[0]
    except IndexError:
        bpy.context.scene.blender_edit_scene_properties.add()

#create channel list
def create_channel_list():
    try:
        bpy.context.scene.blender_edit_scene_properties[0].channellist[0]
    except IndexError:
        bpy.context.scene.blender_edit_scene_properties[0].channellist.add()

#create channels props
def create_channel_props():
    try:
        bpy.context.scene.blender_edit_scene_properties[0].channellist[0].channelprops[0]
    except IndexError:
        for i in range(1,33):
            n=bpy.context.scene.blender_edit_scene_properties[0].channellist[0].channelprops.add()
            n.name="Channel "+str(i)
            n.index=i
            
#get custom props
def get_custom_properties(obj):
    props=[]
    for k in obj.keys():
        props.append(k)
    return props

#get colors
def get_strip_colors():
    prefs=get_addon_preferences()
    colors=[]
    colors.append(prefs.scolor1)
    colors.append(prefs.scolor2)
    colors.append(prefs.scolor3)
    colors.append(prefs.scolor4)
    colors.append(prefs.scolor5)
    colors.append(prefs.scolor6)
    colors.append(prefs.scolor7)
    colors.append(prefs.scolor8)
    colors.append(prefs.scolor9)
    colors.append(prefs.scolor10)
    colors.append(prefs.scolor11)
    colors.append(prefs.scolor12)
    return colors

#create custom prop
def create_custom_property(obj, prop, value):
    obj[prop]=value
    
#clear custom prop
def clear_custom_property(obj, prop):
    del obj[prop]
    
# return playing function
def return_playing_function():
    scn=bpy.context.scene
    cf=scn.frame_current
    playing=[]
    for i in range(32,0,-1):
        for s in scn.sequence_editor.sequences_all:
            if s.frame_final_start<=cf and s.frame_final_end > cf and s.channel==i:
                playing.append(s)
    return playing