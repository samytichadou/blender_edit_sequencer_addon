import bpy

from bpy import props

class ChannelProperties(bpy.types.PropertyGroup):
    name = props.StringProperty()
    index = props.IntProperty()
    color = props.FloatVectorProperty(subtype='COLOR', size=3, min=0, max=1)

class ChannelList(bpy.types.PropertyGroup):
    channelprops=props.CollectionProperty(type=ChannelProperties)
    
class TempComment(bpy.types.PropertyGroup):
    frame=props.IntProperty()
    to_clear=props.BoolProperty(default=False)
    author=props.StringProperty()
    
class BlenderEditSceneProperties(bpy.types.PropertyGroup):
    channellist=props.CollectionProperty(type=ChannelList)
    tempcomment=props.CollectionProperty(type=TempComment)