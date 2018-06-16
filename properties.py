import bpy

from bpy import props

class ChannelProperties(bpy.types.PropertyGroup):
    name = props.StringProperty()
    index = props.IntProperty()
    color = props.FloatVectorProperty(subtype='COLOR', size=3, min=0, max=1)

class ChannelList(bpy.types.PropertyGroup):
    channelprops=props.CollectionProperty(type=ChannelProperties)
    
class BlenderEditSceneProperties(bpy.types.PropertyGroup):
    channellist=props.CollectionProperty(type=ChannelList)