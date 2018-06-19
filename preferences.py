import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))


class BlenderEditPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_name

    scolor1 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[0, 0.871367, 1], subtype='COLOR')
    scolor2 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[0.291771, 1, 0], subtype='COLOR')
    scolor3 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0.904661, 0], subtype='COLOR')
    scolor4 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0, 0.000304], subtype='COLOR')
    scolor5 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0, 0.863157], subtype='COLOR')
    scolor6 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[0.270498, 0, 1], subtype='COLOR')
    scolor7 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[0, 0.194618, 1], subtype='COLOR')
    scolor8 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0.287441, 0], subtype='COLOR')
    scolor9 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0.552011, 0.533276], subtype='COLOR')
    scolor10 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[0.450786, 0.62396, 1], subtype='COLOR')
    scolor11 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 0.879623, 0.53948], subtype='COLOR')
    scolor12 = bpy.props.FloatVectorProperty(min=0.0, max=1.0, default=[1, 1, 1], subtype='COLOR')
    data_base_folder = bpy.props.StringProperty(subtype="DIR_PATH", default=os.path.join(bpy.utils.user_resource('CONFIG'), "blender_edit_database"))

    def draw(self, context):
        layout=self.layout
        layout.prop(self, "data_base_folder")
        box=layout.box()
        box.label("Strip Colors")
        split=box.split()
        col=split.column(align=True)
        col.prop(self, "scolor1", text="")
        col.prop(self, "scolor2", text="")
        col.prop(self, "scolor3", text="")
        col.prop(self, "scolor4", text="")
        col=split.column(align=True)
        col.prop(self, "scolor5", text="")
        col.prop(self, "scolor6", text="")
        col.prop(self, "scolor7", text="")
        col.prop(self, "scolor8", text="")
        col=split.column(align=True)
        col.prop(self, "scolor9", text="")
        col.prop(self, "scolor10", text="")
        col.prop(self, "scolor11", text="")
        col.prop(self, "scolor12", text="")
        
        
# get addon preferences
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)