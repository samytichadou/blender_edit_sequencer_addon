# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 3
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {  
 "name": "Blender Edit",  
 "author": "Samy Tichadou (tonton)",  
 "version": (0, 1),  
 "blender": (2, 7, 9),  
 "location": "Sequencer",  
 "description": "Editing Helper",  
  "wiki_url": "https://github.com/samytichadou/blender-edit_sequencer-addon/wiki",  
 "tracker_url": "https://github.com/samytichadou/blender-edit_sequencer-addon/issues/new",  
 "category": "Sequencer"}


import bpy
import bgl
import blf
import os
import random
import datetime
import csv
import re
import sys
import subprocess
import json
import shutil
from bpy_extras.io_utils import ImportHelper
from bpy.app.handlers import persistent


class BLeditAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    ffprobe_path = bpy.props.StringProperty(subtype="FILE_PATH")
    
    maximum_old_bin = bpy.props.IntProperty(min=2, max=250, default=10)
    
    autosave_frequency = bpy.props.IntProperty(min=1, max=120, default=10)
    
    channel_UI_Vcol = bpy.props.FloatVectorProperty(size=4, min=0.0, max=1.0, default=[0.4, 0.4, 1.0, 0.9], subtype='COLOR')
    
    channel_UI_Acol = bpy.props.FloatVectorProperty(size=4, min=0.0, max=1.0,default=[0.5, 1.0, 1.0, 0.9], subtype='COLOR')
    
    channel_UI_offset = bpy.props.IntProperty(min=0, default=0)
    
    still_image_length = bpy.props.IntProperty(min=1, max=120, default=3)
    
    data_base_folder = bpy.props.StringProperty(subtype="DIR_PATH", default=os.path.join(bpy.utils.user_resource('CONFIG'), "blender_edit_database"))
    
    default_framerate = bpy.props.IntProperty(min=1, default=25)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "data_base_folder", text='Path to Blender Edit Database')
        layout.prop(self, "ffprobe_path", text='Path to FFProbe executable')
        layout.prop(self, "maximum_old_bin", text='Maximum number of Old Bin files')
        layout.prop(self, "autosave_frequency", text='Auto Save Bin Frequency (Minutes)')   
        layout.prop(self, "still_image_length", text='Still Image Length (Seconds)')  
        layout.prop(self, "default_framerate", text='Default Framerate')     
        row=layout.row()
        row.prop(self, "channel_UI_Vcol", text='Color of Video Channel in UI')
        row.prop(self, "channel_UI_Acol", text='Color of Audio Channel in UI')
        row.prop(self, "channel_UI_offset", text='Offset of the Sequencer UI')
        
# get addon preferences
def get_addon_preferences():
    addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
    return addon_preferences

#update function path to project vse folder (create if not exist)
def bledit_create_project_folder(self, context):
#    #get addon prefs
#    addon_preferences = get_addon_preferences()
#    cachefolder = addon_preferences.prefs_folderpath
#    path=os.path.abspath(bpy.path.abspath(cachefolder))
    project_path=os.path.abspath(bpy.path.abspath(bpy.data.window_managers['WinMan'].blender_edit_properties[0].project_path))
    backup_path=os.path.join(project_path, "backup_bin")
    supp_path=os.path.join(project_path, "suppressed_bin")
    #path="C:\\Users\\tonton\\Documents\\TAF\\CODE\\work Blender Edit\\project path"
    if os.path.isdir(project_path)==False:
        os.makedirs(project_path)
        os.makedirs(backup_path)
        os.makedirs(supp_path)
        print('Blender Edit --- Project VSE Folder Created')
    else:
        print('Blender Edit --- Project VSE Folder Found')
    
    return  {'FINISHED'}

#update function for opening some bin
def bledit_update_open_close(self, context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    dir=os.path.dirname(props.bin_list[props.active_bin_index].path)
    active=props.bin_list[props.active_bin_index]
    ext=".blck"
    
    if props.bin_list[props.active_bin_index].open==False :
        if os.path.isfile(os.path.join(dir, (active.name+ext)))==True:
            #remove bin content
            for i in range(len(active.bin_content)-1,-1,-1):
                active.bin_content.remove(i)
            print('Blender Edit --- Bin Content Cleared')
            if active.lock==False:
                os.remove(os.path.join(dir, (active.name+ext)))
                print('Blender Edit --- Bin Closed and Unlocked for other users')
            else:
                print('Blender Edit --- Bin Closed')
            if active.modified==True:
                active.modified=False 
    elif props.bin_list[props.active_bin_index].open==True:
        #load content
        bledit_load_active_bin_content(self, context)
        if os.path.isfile(os.path.join(dir, (active.name+ext)))==False:
            open(os.path.join(dir, (active.name+ext)), 'a').close()
            print('Blender Edit --- Bin Opened and Locked for other users')
            #update bin 
        else:
            print('Blender Edit --- Bin Opened')
        if active.modified==True:
            active.modified=False
        try:
            active.bin_content[active.active_item_index].selected=True
        except IndexError:
            pass      

#update function to put bin modified prop ON
def bledit_update_modified_bin(self, context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active=props.bin_list[props.active_bin_index]
    if active.modified==False:
        active.modified=True
        
#update function to rename bin
def bledit_update_name_bin(self, context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active=props.bin_list[props.active_bin_index]
    old=active.path
    new=os.path.join(os.path.dirname(old), active.name+".bb")
    os.rename(old, new)
    active.path=new
    if os.path.isfile(os.path.splitext(old)[0]+".blck")==True:
        os.remove(os.path.splitext(old)[0]+".blck")
        open((os.path.splitext(new)[0]+".blck"), 'a').close()

#update function to select item
def bledit_update_item_selection(self, context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active_bin=props.bin_list[props.active_bin_index]
    ct=0
    for c in active_bin.bin_content:
        if c.selected==True:
            ct+=1
    if ct==1:
        for c in active_bin.bin_content:
            c.selected=False
    active_bin.bin_content[active_bin.active_item_index].selected=True
        
    
#create new empty bin operator with unique index
class BleditCreateBin(bpy.types.Operator):
    bl_idname = "bledit.create_bin"
    bl_label = "Create Bin"
    bl_options = {'REGISTER', 'UNDO'}

    files = bpy.props.CollectionProperty(name='files', type=bpy.types.OperatorFileListElement)
    directory = bpy.props.StringProperty(subtype='DIR_PATH', default="")
        
    def execute(self, context):
    #    #get addon prefs
    #    addon_preferences = get_addon_preferences()
    #    cachefolder = addon_preferences.prefs_folderpath
    #    path=os.path.abspath(bpy.path.abspath(cachefolder))
        project_path=os.path.abspath(bpy.path.abspath(bpy.data.window_managers['WinMan'].blender_edit_properties[0].project_path))
        bledit_create_project_folder(self, context)
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        ext=".bb"
        bbfiles=[]
        
        for i in range(len(self.files)-1,-1,-1):
            self.files.remove(i)
        self.directory=""
        
        for f in os.listdir(project_path):
            if os.path.isfile(os.path.join(project_path,f))==True and ext in f:
                print(f)
                bbfiles.append(f)
        newct=len(bbfiles)+1
        if os.path.isfile("new_bin_"+str(newct)+ext)==False:
            nbin=os.path.join(project_path, "new_bin_"+str(newct)+ext)
        
        nfile = open(nbin, "w")
        nfile.write("Blender Edit Bin File"+"\n\n")
        nfile.write("__idx___"+str(random.randint(00000, 99999))+"\n")
        nfile.write("__origin___"+bpy.path.basename(bpy.data.filepath)+"\n")
        nfile.write("__creation___"+str(datetime.datetime.now()).split(".")[0]+"\n")
        nfile.close()
        
        print("Blender Edit --- New Bin Created")
        
        newb=self.files.add()
        newb.name=bpy.path.basename(nbin)
        self.directory=project_path
        
        bledit_read_bin(self.files, self.directory, context)
        props.active_bin_index=len(props.bin_list)-1
        
        return {'FINISHED'}


#import helper open bin
### Import Preset Operator ###
class BleditOpenBin(bpy.types.Operator, ImportHelper):
    bl_idname = "bledit.open_bin"
    bl_label = "Open Bin"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".bb"
    filter_glob = bpy.props.StringProperty(default="*.bb", options={'HIDDEN'})
    #filepath = bpy.props.StringProperty(default=os.path.join(bpy.path.abspath("//"), "blender_edit"))
    files = bpy.props.CollectionProperty(name='files', type=bpy.types.OperatorFileListElement)
    directory = bpy.props.StringProperty(subtype='DIR_PATH', default='')
    
    ##### prop #####
#    import_addons_files = BoolProperty(
#            name="Install Addons Files",
#            description="Install Addon Files contained in the CatHide preset File",
#            default=False,
#            )
    
#    #### DRAW ####
#    def draw(self, context):
#        layout = self.layout
#                
#        box = layout.box()
#        box.label('Import Settings :', icon='SCRIPTWIN')
            
    def execute(self, context):
        return bledit_read_bin(self.files, self.directory, context)
    
### IMPORT MENU
def bledit_open_bin(self, context):
    self.layout.operator('bledit.open_bin', text="Open Blender Edit Bin")
    
#read bin file
def bledit_read_bin(files, directory, context):
    bin_list=bpy.data.window_managers['WinMan'].blender_edit_properties[0].bin_list
    lines=[]
    
    for f in files:
        chk=0
        del lines[:]   
        bin_file=os.path.join(directory, f.name) 
        with open(bin_file, 'r', newline='') as csvfile:
            line = csv.reader(csvfile, delimiter='\n')
            for l in line:
                l1=str(l).replace("[", "")
                l2=l1.replace("]", "")
                l3=l2.replace("'", "")
                l4=l3.replace('"', "")
                lines.append(l4)
        for l in lines:
            if "__idx___" in l:
                for b in bin_list:
                    if b.idx==int(l.split("___")[1]):
                        chk=1
        if chk==0:
            
            newbin=bin_list.add()
            
            for l in lines:
                if "__idx___" in l:
                    newbin.idx=int(l.split("___")[1])
                elif "__origin___" in l:
                    newbin.origin=l.split("___")[1]
                elif "__creation___" in l:
                    newbin.creation=l.split("___")[1]

            newbin.modification=os.path.getmtime(bin_file)
            newbin.name=bpy.path.basename(bin_file).split(".bb")[0]
            newbin.path=bin_file
            
            for f in os.listdir(directory):
                if newbin.name+".blck"==f:
                    newbin.lock=True
            
            for a in bpy.context.screen.areas:
                a.tag_redraw()
            print('Blender Edit --- Bin Imported')
        else:
            print('Blender Edit --- Bin already Imported')

    return {'FINISHED'} 


#load active bin content
def bledit_load_active_bin_content(self, context):
    project_path=os.path.abspath(bpy.path.abspath(bpy.data.window_managers['WinMan'].blender_edit_properties[0].project_path))
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active=props.bin_list[props.active_bin_index]
    active_content=active.bin_content
    
    if os.path.isfile(active.path)==True:
        chk=0
        lines=[]
        content=[]
        with open(active.path, 'r', newline='') as csvfile:
            line = csv.reader(csvfile, delimiter='\n')
            for l in line:
                l1=str(l).replace("[", "")
                l2=l1.replace("]", "")
                l3=l2.replace("'", "")
                l4=l3.replace('"', "")
                lines.append(l4)
        for l in lines:
            if "__idx___" in l:
                if int(l.split("__idx___")[1])==active.idx:
                    chk=1
        if chk==1:
            for l in lines:
                if "||" in l:
                    content.append(l)
            for c in content:
                new=active_content.add()
                new.name=c.split("||")[1]
                new.path=os.path.abspath(c.split("||")[2])
                new.type=c.split("||")[3]
                new.idx=int(c.split("||")[5])
                
                new_length=new.length.add()
                new_start=new.start.add()
                new_end=new.end.add()
                new_length.hours=int((c.split("||")[4]).split("|")[0])
                new_length.minutes=int((c.split("||")[4]).split("|")[1])
                new_length.seconds=int((c.split("||")[4]).split("|")[2])
                new_length.frames=int((c.split("||")[4]).split("|")[3])
                new_length.total_frames=int((c.split("||")[4]).split("|")[4])
                try :
                    new_start.hours=int((c.split("|st|")[1]).split("|")[0])
                    new_start.minutes=int((c.split("|st|")[1]).split("|")[1])
                    new_start.seconds=int((c.split("|st|")[1]).split("|")[2])
                    new_start.frames=int((c.split("|st|")[1]).split("|")[3])
                except IndexError:
                    pass
                try : 
                    new_end.hours=int((c.split("|en|")[1]).split("|")[0])
                    new_end.minutes=int((c.split("|en|")[1]).split("|")[1])
                    new_end.seconds=int((c.split("|en|")[1]).split("|")[2])
                    new_end.frames=int((c.split("|en|")[1]).split("|")[3])
                except IndexError:
                    pass
                
                new.x_resolution=int(c.split("||")[6].split("X")[0])
                new.y_resolution=int(c.split("||")[6].split("X")[1])
                new.framerate=int(c.split("||")[7])
                new.codec=c.split("||")[8]
                new.colordepth=int(c.split("||")[9])
                new.color_space=c.split("||")[10]
                new.bitrate=int(c.split("||")[11])
                new.audio_codec=c.split("||")[12]
                new.audio_layout=c.split("||")[13]
                new.audio_channels=int(c.split("||")[14])
                new.audio_sample_rate=int(c.split("||")[15])
                
                if "||c|" in c:
                    for nc in range (1, len(c.split("||c|"))):
                        new_comment=new.comment.add()
                        new_comment.name=c.split("||c|")[nc].split("**")[0]
                        new_comment.creation=c.split("**")[1].split("*")[0]
                        try:
                            new_comment.author=c.split("**")[2].split("*")[0]
                        except IndexError:
                            pass

    print("Blender Edit --- Bin Content Loaded")
    
    return {'FINISHED'}

#refresh bin
class BleditRefreshBin(bpy.types.Operator):
    bl_idname = "bledit.refresh_bin"
    bl_label = "Refresh active Bin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        for i in range(len(active_bin.bin_content)-1,-1,-1):
            active_bin.bin_content.remove(i)
        bledit_load_active_bin_content(self, context)
        try:
            active_bin.bin_content[active_bin.active_item_index].selected=True
        except IndexError:
            pass
        active_bin.modified=False
        print('Blender Edit --- Bin content reloaded')
    
        return {'FINISHED'}

#import helper immport content
class BleditImportContent(bpy.types.Operator, ImportHelper):
    bl_idname = "bledit.import_content"
    bl_label = "Import Content"
    bl_options = {'REGISTER', 'UNDO'}
    
    #filename_ext = ".bb"
    #filter_glob = bpy.props.StringProperty(default="*.bb", options={'HIDDEN'})
    files = bpy.props.CollectionProperty(name='files', type=bpy.types.OperatorFileListElement)
    directory = bpy.props.StringProperty(subtype='DIR_PATH', default='')
    
    ##### prop #####
#    import_addons_files = BoolProperty(
#            name="Install Addons Files",
#            description="Install Addon Files contained in the CatHide preset File",
#            default=False,
#            )

    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
        except IndexError:
            chk=1
        return chk==0 and active_bin.open==True and active_bin.lock==False
    
    #### DRAW ####
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        layout = self.layout
        layout.label('Import Settings :', icon='SCRIPTWIN')
        box=layout.box()
        box.label("Image Sequence")
        box.prop(props, "auto_detect_image_sequence", text="Detect Image Sequence")
        box.prop(props, "minimum_image_sequence", text="Number of Image")
            
    def execute(self, context):
        return bledit_import_content(self.files, self.directory, context)

def bledit_import_content(files, directory, context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    #change this with addon_prefs
    auto_seq=props.auto_detect_image_sequence
    bin_list=props.bin_list
    active_bin=bin_list[props.active_bin_index]
    ct=0
    # order to get video infos 
        # width 0 , height 1 , length 2 , codec 3 , framerate 4 , color_space 5 , bitrate 6 , colordepth 7 , audio_channels 8 
        # sample_rate 9 , audio_layout 10 , audio_codec 11
    for f in files:
        ct=ct+1
        print("Blender Edit --- Importing File "+str(ct)+"/"+str(len(files)))
        if f.name not in [c.name for c in active_bin.bin_content]:
            chk=0
            filepath=os.path.join(directory, f.name)
            h,m,s,fr,l=0,0,0,0,0
            if getFileType(filepath)!="unknown":
                type=getFileType(filepath)
                if type=='Image Sequence' and auto_seq==True:
                    name, seq_length, path=ResolveImageSequence(filepath)
                    for f2 in active_bin.bin_content:
                        if f2.name in name:
                            chk=1
                    h,m,s,fr=ConvertFramesToTimecode(int(seq_length))
                    l=seq_length
                else:
                    name=str(f.name)
                    path=filepath
                    if type=='Image':
                        h=m=s=0
                        fr=l=1
                    else:    
                        l=int(find_video_metadata(path)[2])
                        h,m,s,fr=ConvertFramesToTimecode(l)
                if chk==0:
                    new=active_bin.bin_content.add()
                    new.name=name
                    new.path=os.path.abspath(path)
                    new.type=type
                    new.idx=random.randint(00000, 99999)
                    new.length.add()
                    new.length[0].hours=h
                    new.length[0].minutes=m
                    new.length[0].seconds=s
                    new.length[0].frames=fr
                    new.length[0].total_frames=l
                    new.start.add()
                    new.end.add()
                    
                    new.x_resolution=find_video_metadata(path)[0]
                    new.y_resolution=find_video_metadata(path)[1]
                    new.codec=find_video_metadata(path)[3]
                    new.framerate=find_video_metadata(path)[4]
                    new.color_space=find_video_metadata(path)[5]
                    new.bitrate=find_video_metadata(path)[6]
                    new.colordepth=find_video_metadata(path)[7]
                    new.audio_channels=find_video_metadata(path)[8]
                    new.audio_sample_rate=find_video_metadata(path)[9]
                    if find_video_metadata(path)[10] in {"none", "stereo", "mono"}:
                        new.audio_layout=find_video_metadata(path)[10]
                    else:
                        new.audio_layout="unknown"
                    new.audio_codec=find_video_metadata(path)[11]
                    for c in active_bin.bin_content:
                        c.selected=False
                    new.selected=True
                    
                    active_bin.active_item_index=len(active_bin.bin_content)-1
                    
                if active_bin.modified==False:
                    active_bin.modified=True
            else:
                print("Blender Edit --- Uncompatible File")
        else:
            print("Blender Edit --- File Already imported in this bin")
    return {'FINISHED'}

#get file type
def getFileType(filepath):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    auto_seq=props.auto_detect_image_sequence
    min_seq=props.minimum_image_sequence
    Video={"mpg","mpeg","dvd","vob","mp4","avi","mov","dv","ogg","ogv","mkv","flv",
            "MPG","MPEG","DVD","VOB","MP4","AVI","MOV","DV","OGG","OGV","MKV","FLV"}
    Audio={"wav","mp3","mp2","ac3","aac","oga","flac","pcm",
            "WAV","MP3","MP2","AC3","AAC","OGA","FLAC","PCM"}
    Image={"bmp","sgi","rgb","bw","png","jpg","jpeg","jp2","j2c","tga","cin",
            "dpx","exr","hdr","tif","tiff","psd",
            "BMP","SGI","RGB","BW","PNG","JPG","JPEG","JP2","J2C","TGA","CIN",
            "DPX","EXR","HDR","TIF","TIFF","PSD",}
    type="unknown"
    file=os.path.split(filepath)[1]
    for n in file.split("."):
        if any(n in v for v in Video):
            type="Video"
        elif any(n in v for v in Audio):
            type="Audio"
        elif any(n in v for v in Image):
            if len(ResolveImageSequence(filepath))==1 or auto_seq==False or int(ResolveImageSequence(filepath)[1])<min_seq:
                type="Image"
            else:
                type="Image Sequence"
    return (type)

#get video info
def find_video_metadata(video_path: str):
    """Find the resolution of the input video file."""
    addon_preferences = get_addon_preferences()
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    ffprobe=addon_preferences.ffprobe_path
    args = [ffprobe] + "-v quiet -print_format json -show_streams".split() + [video_path]

    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffout = subprocess.check_output(args).decode('utf-8')
    ffinfo = json.loads(ffout)

    # prints all the metadata available:
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(ffinfo)
    
    #variables
    height = 0
    width = 0
    length = 0
    codec = "none"
    framerate = 0
    color_space = "none"
    bitrate = 0
    colordepth = 0
    audio_channels = 0
    sample_rate = 0
    audio_layout = "none"
    audio_codec = "none"
    
    # for example, find height and width
    for n in ffinfo['streams']:
        if n['codec_type']=='video':
            height = int(n['height'])
            width = int(n['width'])
            try:
                length = int(n['nb_frames'])
            except KeyError:
                pass
            codec = n['codec_name']
            framerate = int(n['r_frame_rate'].split("/")[0])
            try:
                color_space = n['color_space']
            except KeyError:
                pass
            try:
                bitrate = int(n['bit_rate'])
            except KeyError:
                pass
            colordepth = int(n['bits_per_raw_sample'])
        elif n['codec_type']=='audio':
            audio_channels = int(n['channels'])
            sample_rate = int(n['sample_rate'])
            try:
                audio_layout = n['channel_layout']
            except KeyError:
                pass
            audio_codec = n['codec_name']  

    return width, height, length, codec, framerate, color_space, bitrate, colordepth, audio_channels, sample_rate, audio_layout, audio_codec

#find image sequence
def ResolveImageSequence(filepath):
    basedir, filename = os.path.split(os.path.abspath(bpy.path.abspath(filepath)))
    filename_noext, ext = os.path.splitext(filename)
    seq=[]
    from string import digits
    if isinstance(filepath, bytes):
        digits = digits.encode()
    filename_nodigits = filename_noext.rstrip(digits)

    if len(filename_nodigits) == len(filename_noext):
        # input isn't from a sequence
        return ["False"]
    
    else:
        for f in os.scandir(basedir):
            if f.is_file():
                if f.name.startswith(filename_nodigits) and f.name.endswith(ext):
                    if f.name[len(filename_nodigits):-len(ext) if ext else -1].isdigit():
                        seq.append(f.name)
        path=os.path.join(basedir, seq[0])
        return [filename_nodigits, len(seq), path]

#convert frame to timecode
def ConvertFramesToTimecode(length):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    fps=props.project_framerate
    seconds, f = divmod(length, fps)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return [h,m,s,f]


#add new comment
class BleditAddComment(bpy.types.Operator):
    bl_idname = "bledit.add_comment"
    bl_label = "Add Comment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        new_comment=active_item.comment.add()
        new_comment.name=props.temporary_comment
        new_comment.author=props.temporary_comment_author
        new_comment.creation=str(datetime.datetime.now()).split(".")[0]
        props.property_unset("temporary_comment")
        if active_bin.modified==False:
            active_bin.modified=True
        print("Blender Edit --- Comment Added")
    
        return {'FINISHED'}

#save bin operator
class BleditSaveActiveBin(bpy.types.Operator):
    bl_idname = "bledit.save_active_bin"
    bl_label = "Save Bin"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
        except IndexError:
            chk=1
        return chk==0 and active_bin.open==True and active_bin.lock==False and active_bin.modified==True

    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        addon_preferences = get_addon_preferences()
        max_old=addon_preferences.maximum_old_bin
        active_bin=props.bin_list[props.active_bin_index]
        basedir, oldname=os.path.split(active_bin.path)
        ext=".bb"
        nbin = os.path.join(basedir, active_bin.name+ext)
        backup = os.path.join(basedir, "backup_bin")
        
        if os.path.isfile(active_bin.path):
            #backup
            ct=0
            if os.path.isdir(backup)==False:
                os.makedirs(backup)
            for file in os.listdir(os.path.join(basedir, "backup_bin")):
                if active_bin.name+"_old" in file:
                    ct=ct+1
            if ct>=max_old:
                diff=(ct-max_old)+1
                ct2=0
                for n in range(0, diff):
                    os.remove(os.path.join(backup, active_bin.name+"_old"+str(n).zfill(3)+ext))
                for file in sorted(os.listdir(os.path.join(basedir, "backup_bin"))):
                    print(file)
                    if active_bin.name+"_old" in file:
                        print(str(ct2))
                        os.rename(os.path.join(backup, file), os.path.join(backup, active_bin.name+"_old"+str(ct2).zfill(3)+ext))
                        ct2=ct2+1
                ct=ct-1
            shutil.copyfile(active_bin.path, os.path.join(backup, active_bin.name+"_old"+str(ct).zfill(3)+ext))
            #clean old
            os.remove(active_bin.path)
            
        nfile = open(nbin, "w")
        nfile.write("Blender Edit Bin File"+"\n\n")
        nfile.write("__idx___"+str(active_bin.idx)+"\n")
        nfile.write("__origin___"+active_bin.origin+"\n")
        nfile.write("__creation___"+active_bin.creation)
        for n in active_bin.bin_content:
            nfile.write("\n||"+n.name+"||"+os.path.abspath(n.path)+"||"+n.type)
            nfile.write("||"+str(n.length[0].hours)+"|"+str(n.length[0].minutes)+"|"+str(n.length[0].seconds)+"|"+str(n.length[0].frames)+"|"+str(n.length[0].total_frames))
            nfile.write("|st|"+str(n.start[0].hours)+"|"+str(n.start[0].minutes)+"|"+str(n.start[0].seconds)+"|"+str(n.start[0].frames))
            nfile.write("|en|"+str(n.end[0].hours)+"|"+str(n.end[0].minutes)+"|"+str(n.end[0].seconds)+"|"+str(n.end[0].frames))
            nfile.write("||"+str(n.idx))
            nfile.write("||"+str(n.x_resolution)+"X"+str(n.y_resolution))
            nfile.write("||"+str(n.framerate))
            nfile.write("||"+n.codec)
            nfile.write("||"+str(n.colordepth))
            nfile.write("||"+n.color_space)
            nfile.write("||"+str(n.bitrate))
            
            nfile.write("||"+n.audio_codec)
            nfile.write("||"+str(n.audio_layout))
            nfile.write("||"+str(n.audio_channels))
            nfile.write("||"+str(n.audio_sample_rate))
            for c in n.comment:
                nfile.write("||c|"+c.name+"**"+c.creation+"**"+c.author+"*")
        nfile.close()
        active_bin.modified=False
        
        #create the lock file
        if os.path.isfile(os.path.join(basedir, active_bin.name+".blck"))==False:
            open(os.path.join(basedir, active_bin.name+".blck"), 'a').close()
        
        print("Blender Edit --- Bin Successfully saved")
            
        return {'FINISHED'}
    
#save all bins operator
class BleditSaveAllBins(bpy.types.Operator):
    bl_idname = "bledit.save_all_bins"
    bl_label = "Save All Bins"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        bin_list=bpy.data.window_managers['WinMan'].blender_edit_properties[0].bin_list
        return len(bin_list)!=0

    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        bin_list=props.bin_list
        old_idx=props.active_bin_index
        active_bin=props.bin_list[props.active_bin_index]
        for n in range(0, len(bin_list)):
            if bin_list[n].open==True and bin_list[n].modified==True:
                props.active_bin_index=n
                bpy.ops.bledit.save_active_bin()
        props.active_bin_index=old_idx
    
        return {'FINISHED'}

#modal auto save
class BleditModalAutoSave(bpy.types.Operator):
    bl_idname = "bledit.auto_save"
    bl_label = "Bin Auto Save"
    
    _timer = None
    
    @classmethod
    def poll(cls, context):
        working=bpy.data.window_managers['WinMan'].blender_edit_properties[0].running_autosave
        return working==False
    
    def __init__(self):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        props.running_autosave=True
        print("Blender Edit --- Starting Auto Save Mode")

    def modal(self, context, event):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        
        if props.running_autosave==False:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            chk=0
            bin_list=props.bin_list
            for b in bin_list:
                if b.open==True and b.modified==True:
                    chk=1
            if chk==1:
                self.report({'INFO'}, "Saving")
                print("Blender Edit --- Auto Saving Bins")
                bpy.ops.bledit.save_all_bins()
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        addon_preferences = get_addon_preferences()
        freq=addon_preferences.autosave_frequency
        wm = context.window_manager
        self._timer = wm.event_timer_add(float(freq*60), context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        chk=0
        try:
            props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        except KeyError:
            chk=1
        if chk==0:
            project_path=props.project_path
            bin_list=props.bin_list
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            #close all bins
            ct=-1
            for b in bin_list:
                ct+=1
                if b.open==True:
                    props.active_bin_index=ct
                    b.open=False
                    print("Blender Edit --- Closing "+b.name)
            if os.path.isdir(project_path)==True:
                #clean old blck
                bins = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f)) and ".bb" in f]
                locks = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f)) and ".blck" in f]
                for l in locks:
                    chk=0
                    for b in bins:
                        if os.path.splitext(b)[0]==os.path.splitext(l)[0]:
                            chk=1
                    if chk==0:
                        os.remove(os.path.join(project_path, l))
                        print("Blender Edit --- Cleaning " + l)
        
        print("Blender Edit --- Quitting Auto Save Mode")
        
#copy selected items to other bins
class BleditCopyContent(bpy.types.Operator):
    bl_idname = "bledit.copy_content"
    bl_label = "Copy Content"
    bl_options = {'REGISTER', 'UNDO'}
    
    index=bpy.props.IntProperty()
    
    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        old_index=active_bin.active_item_index
        ct=-1
        if props.bin_list[self.index].open==True:
            for c in active_bin.bin_content:
                ct=ct+1
                chk=0
                if c.selected==True:
                    for c2 in props.bin_list[self.index].bin_content:
                        if c.path==c2.path:
                            chk=1
                    if chk==0:
                        active_bin.active_item_index=ct
                        CopyItemToBin(self.index)
            active_bin.active_item_index=old_index
            print("Blender Edit --- Item(s) Copied")

        return {'FINISHED'}
    
#move selected items to other bins
class BleditMoveContent(bpy.types.Operator):
    bl_idname = "bledit.move_content"
    bl_label = "Move Content"
    bl_options = {'REGISTER', 'UNDO'}
    
    index=bpy.props.IntProperty()
    
    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        old_index=active_bin.active_item_index
        ct=-1
        if props.bin_list[self.index].open==True:
            for c in active_bin.bin_content:
                ct=ct+1
                chk=0
                if c.selected==True:
                    chk=1
                    for c2 in props.bin_list[self.index].bin_content:
                        if c.path==c2.path:
                            chk=2
                    if chk==1:
                        active_bin.active_item_index=ct
                        CopyItemToBin(self.index)
                        active_bin.bin_content.remove(active_bin.active_item_index)
            active_bin.active_item_index=old_index
            print("Blender Edit --- Item(s) Moved")
            
        return {'FINISHED'}
        
#copy active item to other bin
def CopyItemToBin(dest_index):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active_bin=props.bin_list[props.active_bin_index]
    active_item=active_bin.bin_content[active_bin.active_item_index]
    dest=props.bin_list[dest_index].bin_content
    new=dest.add()
    new.length.add()
    new.start.add()
    new.end.add()
    for n in active_item.keys():
        new[n]=active_item[n]
    props.bin_list[dest_index].modified=True

    return {'FINISHED'}


#bin actions
class BleditBinActions(bpy.types.Operator):
    bl_idname = "bledit.bin_actions"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('SUPPRESS', "Suppress", ""),
            ))
    
    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
        except IndexError:
            chk=1
        return chk==0

    def invoke(self, context, event):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        bin_list=props.bin_list
        active=props.bin_list[props.active_bin_index]
        idx=props.active_bin_index

        if self.action == 'DOWN' and idx < len(bin_list) - 1:
            bin_list.move(idx, idx+1)
            props.active_bin_index=idx+1
            
        elif self.action == 'UP' and idx >= 1:
            bin_list.move(idx, idx-1)
            props.active_bin_index=idx-1
            
        elif self.action == 'SUPPRESS' :
            supp=os.path.join(os.path.dirname(active.path), "suppressed_bin")
            if os.path.isfile(active.path)==True:
                shutil.copyfile(active.path, os.path.join(supp, active.name+".bb"))
                os.remove(active.path)
            bin_list.remove(idx)
            if len(bin_list)<=idx:
                props.active_bin_index=len(bin_list)-1
            print("Blender Edit --- Bin Removed")
    
        return {'FINISHED'}
    
#content actions
class BleditContentActions(bpy.types.Operator):
    bl_idname = "bledit.content_actions"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('SUPPRESS', "Suppress", ""),
            ('SELECT/DESELECT', "Select/Deselect All", "")
            ))
    
    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
            active_item=active_bin.bin_content[active_bin.active_item_index]
        except IndexError:
            chk=1
        return chk==0

    def invoke(self, context, event):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        bin_list=props.bin_list
        active_bin=props.bin_list[props.active_bin_index]
        bin_content=active_bin.bin_content
        active=active_bin.bin_content[active_bin.active_item_index]
        idx=active_bin.active_item_index

        if self.action == 'DOWN' and idx < len(bin_content) - 1:
            bin_content.move(idx, idx+1)
            active_bin.active_item_index=idx+1
            
        elif self.action == 'UP' and idx >= 1:
            bin_content.move(idx, idx-1)
            active_bin.active_item_index=idx-1
            
        elif self.action == 'SUPPRESS' :
            bin_content.remove(idx)
            if len(bin_content)<=idx:
                active_bin.active_item_index=len(bin_content)-1
            print("Blender Edit --- Item Removed")
            
        elif self.action == 'SELECT/DESELECT' :
            ct=0
            for n in bin_content:
                if n.selected==True:
                    ct+=1
            if ct==len(bin_content):
                for n in bin_content:
                    n.selected=False
                bledit_update_item_selection(self, context)
            else:
                for n in bin_content:
                    n.selected=True
        
        bledit_update_modified_bin(self, context)
        
        return {'FINISHED'}
    
#comment actions
class BleditCommentActions(bpy.types.Operator):
    bl_idname = "bledit.comment_actions"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('SUPPRESS', "Suppress", ""),
            ))
    
    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
            active_item=active_bin.bin_content[active_bin.active_item_index]
            active_comment=active_item.comment[active_item.active_comment_index]
        except IndexError:
            chk=1
        return chk==0

    def invoke(self, context, event):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        bin_list=props.bin_list
        active_bin=props.bin_list[props.active_bin_index]
        bin_content=active_bin.bin_content
        active_item=active_bin.bin_content[active_bin.active_item_index]
        comment=active_item.comment
        active_comment=active_item.comment[active_item.active_comment_index]
        idx=active_item.active_comment_index

        if self.action == 'DOWN' and idx < len(comment) - 1:
            comment.move(idx, idx+1)
            active_item.active_comment_index=idx+1
            
        elif self.action == 'UP' and idx >= 1:
            comment.move(idx, idx-1)
            active_item.active_comment_index=idx-1
            
        elif self.action == 'SUPPRESS' :
            comment.remove(idx)
            if len(comment)<=idx:
                active_item.active_comment_index=len(comment)-1
            print("Blender Edit --- Comment Removed")
        
        bledit_update_modified_bin(self, context)
        
        return {'FINISHED'}



#import direct link
#import with conversion (test à faire sur format) with ffmpeg in separate threads

#move content from a bin to another bin

#simple import on active media on timeline

#scan project folder for bin

#bin list
class BleditBinList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, flt_flag):
        if item.open==True:
            layout.prop(item, "name", emboss=False, text='')
        else:
            layout.enabled=False
            layout.label(item.name)
        if item.lock==True:
            layout.label("", icon='LOCKED')
        if item.open==True:
            layout.label("", icon='FILESEL')
            
#bin content list
class BleditBinContentList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, flt_flag):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active=props.bin_list[props.active_bin_index]
        active_item=active.bin_content[active.active_item_index]
        if item.type=="Image":
            layout.label(icon='FILE_IMAGE')
        elif item.type=="Video":
            layout.label(icon='FILE_MOVIE')
        elif item.type=="Audio":
            layout.label(icon='FILE_SOUND')
        elif item.type=="Image Sequence":
            layout.label(icon='IMAGE_COL')
        elif item.type=="Timeline":
            layout.label(icon='SEQ_SEQUENCER')
        if active.lock==False:
            layout.prop(item, "name", emboss=False, text='')
            if len(item.comment)!=0:
                layout.label(icon='TEXT')
            layout.prop(item, "selected", text='')
        else:
            layout.enabled=False
            layout.label(item.name)
            if len(item.comment)!=0:
                layout.label(icon='TEXT')
            layout.label("", icon='LOCKED')

#Comment list
class BleditCommentList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, flt_flag):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active=props.bin_list[props.active_bin_index]
        active_item=active.bin_content[active.active_item_index]
        
        if active.lock==False:
            layout.prop(item, "name", emboss=False, text='')
            layout.prop(item, "author", emboss=False, text='')
            layout.label(item.creation)
        else:
            layout.enabled=False
            layout.label(item.name)
            layout.label(item.author)
            layout.label(item.creation)
            layout.label("", icon='LOCKED')
        

#Overwrite on Timeline
class BleditOverwriteOnTimeline(bpy.types.Operator):
    bl_idname = "bledit.overwrite_on_timeline"
    bl_label = "Overwrite on Timeline"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=props.bin_list[props.active_bin_index].bin_content[active_bin.active_item_index]
        oindex=active_bin.active_item_index
        addon_preferences = get_addon_preferences()
        oframe=bpy.context.scene.frame_current
        
        #fct to create sequencer
        BleditCreateSequencer()
        
        OverwriteOnTimeline(0)
        if active_item.type=="Image":
            lgt=addon_preferences.still_image_length*props.project_framerate
        else:
            lgt=active_item.length[0].total_frames
        #bpy.context.scene.frame_current=bpy.context.scene.frame_current+lgt
        ct=-1
        for c in active_bin.bin_content:
            ct+=1
            if c.selected==True and ct!=oindex:
                bpy.context.scene.frame_current=bpy.context.scene.frame_current+lgt
                if c.type=="Image":
                    lgt=addon_preferences.still_image_length*props.project_framerate
                else:
                    lgt=active_item.length[0].total_frames
                active_bin.active_item_index=ct
                OverwriteOnTimeline(ct+1)
                
        active_bin.active_item_index=oindex
        if propscene.use_in==True:
            bpy.context.scene.frame_current=propscene.in_point
        else:
            bpy.context.scene.frame_current=oframe
        
        return {'FINISHED'}
    
#overwrite active item on timeline function
def OverwriteOnTimeline(index):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    propscene=bpy.context.scene.blender_edit_scene_properties[0]
    active_bin=props.bin_list[props.active_bin_index]
    active=active_bin.bin_content[active_bin.active_item_index]
    current_frame=bpy.context.scene.frame_current
    video_c=propscene.active_video_channel
    audio_c=propscene.active_audio_channel
    scname=bpy.context.scene.name
    scene=bpy.context.scene
    addon_preferences = get_addon_preferences()
    
    chk=0
    
    u_in=propscene.use_in
    u_out=propscene.use_out
    inp=propscene.in_point
    outp=propscene.out_point
    
    if u_in==True and u_out==True and inp<outp:

        chk=1
        if index==0:
            scene.frame_current=inp
        lgtIO=outp-scene.frame_current
        if active.type=="Image":
            lgt=addon_preferences.still_image_length*props.project_framerate
            if lgt>lgtIO:
                lgt=lgtIO
            DeleteStripsOnLocation(lgt, video_c)
        else:
            lgt=active.length[0].total_frames
            if lgt>lgtIO:
                lgt=lgtIO
            if active.type=="Audio":
                DeleteStripsOnLocation(lgt, audio_c)
            else:
                if active.type=="Video" and active.audio_channels!=0:
                    DeleteStripsOnLocation(lgt, audio_c)
                DeleteStripsOnLocation(lgt, video_c)
        
    elif u_in==True:
            
        if index==0:
            scene.frame_current=inp
        if active.type=="Image":
            lgt=addon_preferences.still_image_length*props.project_framerate
            DeleteStripsOnLocation(lgt, video_c)
        else:
            lgt=active.length[0].total_frames
            if active.type=="Audio":
                DeleteStripsOnLocation(lgt, audio_c)
            else:
                if active.type=="Video" and active.audio_channels!=0:
                    DeleteStripsOnLocation(lgt, audio_c)
                DeleteStripsOnLocation(lgt, video_c)
                
    elif u_out==True and scene.frame_current<outp:

        chk=1
        lgtIO=outp-scene.frame_current
        if active.type=="Image":
            lgt=addon_preferences.still_image_length*props.project_framerate
            if lgt>lgtIO:
                lgt=lgtIO
            DeleteStripsOnLocation(lgt, video_c)
        else:
            lgt=active.length[0].total_frames
            if lgt>lgtIO:
                lgt=lgtIO
            if active.type=="Audio":
                DeleteStripsOnLocation(lgt, audio_c)
            else:
                if active.type=="Video" and active.audio_channels!=0:
                    DeleteStripsOnLocation(lgt, audio_c)
                DeleteStripsOnLocation(lgt, video_c)
        
    else:

        if active.type=="Image":
            lgt=addon_preferences.still_image_length*props.project_framerate
            DeleteStripsOnLocation(lgt, video_c)
        else:
            lgt=active.length[0].total_frames
            if active.type=="Audio":
                DeleteStripsOnLocation(lgt, audio_c)
            else:
                if active.type=="Video" and active.audio_channels!=0:
                    DeleteStripsOnLocation(lgt, audio_c)
                DeleteStripsOnLocation(lgt, video_c)

    #new strip
    if chk==1 and scene.frame_current>=outp:
        print("Blender Edit --- Item(s) not Imported : no more space in specified area")
    else:
        bpy.ops.sequencer.select_all(action='DESELECT')
        if active.type=="Image":
            new=bpy.context.scene.sequence_editor.sequences.new_image(active.name, active.path, video_c, scene.frame_current)
            new.frame_final_duration=lgt
        elif active.type=="Video":
            new=bpy.context.scene.sequence_editor.sequences.new_movie(active.name, active.path, video_c, scene.frame_current)
            new.frame_final_duration=lgt
            if active.audio_channels!=0:
                new_sound=bpy.context.scene.sequence_editor.sequences.new_sound(active.name, active.path, audio_c, scene.frame_current)
                new_sound.frame_final_duration=lgt
                new_sound.select=True
        elif active.type=="Audio":
            new=bpy.context.scene.sequence_editor.sequences.new_sound(active.name, active.path, audio_c, scene.frame_current)
            new.frame_final_duration=lgt
        elif active.type=="Image Sequence":
            new=bpy.context.scene.sequence_editor.sequences.new_image(active.name, active.path, video_c, scene.frame_current)
            #add element
            ct=0
            for file in os.listdir(os.path.split(active.path)[0]):
                if active.name in file and ct<lgt:
                    new.elements.append(file)
                    ct+=1
                elif ct==lgt:
                    break
            new.frame_final_duration=lgt
            
        print("Blender Edit --- Item(s) Imported on Timeline")
        
#    #cut new strip according to IN OUT
#    if chk==1:
#        print("cut")
#        new.select=True
#        scene.frame_current=outp
#        bpy.ops.sequencer.cut(frame=current_frame, type='SOFT', side='RIGHT')
#        bpy.ops.sequencer.delete()
#        new.channel=video_c
#        if chka==1:
#            new_sound.channel=audio_c
    
        bpy.context.scene.sequence_editor.active_strip = new
        
    return {'FINISHED'}

def DeleteStripsOnLocation(lgt, channel):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    active_bin=props.bin_list[props.active_bin_index]
    active=active_bin.bin_content[active_bin.active_item_index]
    current_frame=bpy.context.scene.frame_current
    scname=bpy.context.scene.name
    end=current_frame+lgt

    #bpy.context.scene.sequence_editor.active_strip = None
    #bpy.ops.sequencer.refresh_all()
    bpy.ops.sequencer.select_all(action='DESELECT')
    for s in bpy.context.scene.sequence_editor.sequences_all:
        st=s.frame_start+s.frame_offset_start
        en=st+s.frame_final_duration
        if s.channel==channel:
            if st<current_frame and en<=end and en>current_frame:
                s.select=True
                #bpy.ops.sequencer.cut(frame=current_frame, type='SOFT', side='LEFT')
            elif st>=current_frame and en>=end and st<=end:
                s.select=True
                #bpy.ops.sequencer.cut(frame=end, type='SOFT', side='LEFT')
            elif st<current_frame and en>end:
                s.select=True
                #bpy.ops.sequencer.cut(frame=current_frame-1, type='SOFT', side='RIGHT')
                #bpy.ops.sequencer.cut(frame=end, type='SOFT', side='LEFT')
    bpy.ops.sequencer.cut(frame=current_frame, type='SOFT', side='RIGHT')
    
    bpy.ops.sequencer.select_all(action='DESELECT')
    for s in bpy.context.scene.sequence_editor.sequences_all:
        st=s.frame_start+s.frame_offset_start
        en=st+s.frame_final_duration
        if s.channel==channel:
            if st<current_frame and en>end:
                s.select=True
                #bpy.ops.sequencer.cut(frame=current_frame-1, type='SOFT', side='RIGHT')
                #bpy.ops.sequencer.cut(frame=end, type='SOFT', side='LEFT')
            elif st>=current_frame and en>current_frame+lgt and st<=current_frame+lgt:
                s.select=True
    bpy.ops.sequencer.cut(frame=end, type='SOFT', side='LEFT')
    
    #bpy.ops.sequencer.refresh_all()
    bpy.ops.sequencer.select_all(action='DESELECT')
    for s in bpy.data.scenes[scname].sequence_editor.sequences_all:
        st=s.frame_start+s.frame_offset_start
        en=st+s.frame_final_duration
        if s.channel==channel:
            if st>=current_frame and en<=current_frame+lgt:
                s.select=True
    bpy.ops.sequencer.delete()

    #bpy.ops.sequencer.refresh_all()
#    for s in bpy.data.scenes[scname].sequence_editor.sequences_all:
#        st=s.frame_start+s.frame_offset_start
#        en=st+s.frame_final_duration
#        if s.channel==channel:
#            bpy.ops.sequencer.select_all(action='DESELECT')
#            s.select=True
#            if st<=current_frame and en>current_frame and en<=current_frame+lgt:
#                s.frame_final_duration=(current_frame-st)
#            elif st>=current_frame and en>current_frame+lgt and st<=current_frame+lgt:
#                s.frame_offset_start=s.frame_offset_start+((current_frame+lgt)-st)
    
    return {'FINISHED'}

#Replace on Timeline
#class BleditReplaceOnTimeline(bpy.types.Operator):
#    bl_idname = "bledit.replace_on_timeline"
#    bl_label = "Replace on Timeline"
#    bl_options = {'REGISTER', 'UNDO'}
#    
#    def execute(self, context):
#        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
#        propscene=bpy.context.scene.blender_edit_scene_properties[0]
#        active_bin=props.bin_list[props.active_bin_index]
#        active_item=props.bin_list[props.active_bin_index].bin_content[active_bin.active_item_index]
#        index=active_bin.active_item_index
#        current_frame=bpy.context.scene.frame_current
#        scene=bpy.context.scene
#        addon_preferences = get_addon_preferences()
#        
#        chk=0
#        chka=0
#        #fct to create sequencer
#        BleditCreateSequencer()
#        if active_item.type=="Image":
#            lgt=addon_preferences.still_image_length*props.project_framerate
#        else:
#            lgt=active_item.length[0].total_frames
#        
#        #bpy.ops.sequencer.refresh_all()
#        
#        if active_item.type=='Audio':
#            channel=propscene.active_audio_channel
#        else:
#            channel=propscene.active_video_channel
#        bpy.ops.sequencer.select_all(action='DESELECT')
#        for s in scene.sequence_editor.sequences_all:
#            st=s.frame_start+s.frame_offset_start
#            en=st+s.frame_final_duration
#            if s.channel==channel:
#                if st<=current_frame and en>current_frame:
#                    chk=1
#                    s.select=True
#                    start=st
#                    end=en
#                    rstart=s.frame_start

#        if active_item.type=='Video' and active_item.audio_channels!=0:
#            for s in scene.sequence_editor.sequences_all:
#                sta=s.frame_start+s.frame_offset_start
#                ena=sta+s.frame_final_duration
#                if s.channel==propscene.active_audio_channel:
#                    if sta<=current_frame and ena>current_frame:
#                        chka=1
#                        #bpy.ops.sequencer.select_all(action='DESELECT')
#                        s.select=True
#                        astart=sta
#                        aend=ena
#                        rastart=s.frame_start
#        
#        bpy.ops.sequencer.delete()
#        
#        bpy.ops.sequencer.select_all(action='DESELECT')
#        if chk==1:
#            if active_item.type=="Image":
#                new=scene.sequence_editor.sequences.new_image(active_item.name, active_item.path, channel, rstart)
#                new.select=True
#            elif active_item.type=="Video":
#                if active_item.audio_channels!=0 and chka==1:
#                    new_sound=bpy.context.scene.sequence_editor.sequences.new_sound(active_item.name, active_item.path, propscene.active_audio_channel, rastart)
#                    new_sound.select=True
#                    bpy.ops.sequencer.cut(frame=astart, type='SOFT', side='RIGHT')
#                    bpy.ops.sequencer.cut(frame=aend, type='SOFT', side='RIGHT')
#                bpy.ops.sequencer.select_all(action='DESELECT')
#                new=scene.sequence_editor.sequences.new_movie(active_item.name, active_item.path, channel, rstart)
#                new.select=True
#            elif active_item.type=="Audio":
#                new=scene.sequence_editor.sequences.new_sound(active_item.name, active_item.path, channel, rstart)
#                new.select=True
#            elif active_item.type=="Image Sequence":
#                new=scene.sequence_editor.sequences.new_image(active_item.name, active_item.path, channel, rstart)
#                #add element
#                ct=0
#                for file in os.listdir(os.path.split(active_item.path)[0]):
#                    if active_item.name in file and ct<lgt:
#                        new.elements.append(file)
#                        ct+=1
#                    elif ct==lgt:
#                        break
#                new.select=True
#            bpy.ops.sequencer.cut(frame=start, type='SOFT', side='RIGHT')
#            bpy.ops.sequencer.cut(frame=end, type='SOFT', side='RIGHT')
#            
#        elif chka==1 and chk==0:
#            new=bpy.context.scene.sequence_editor.sequences.new_sound(active_item.name, active_item.path, propscene.active_audio_channel, rastart)
#            new.select=True
#            bpy.ops.sequencer.cut(frame=astart, type='SOFT', side='RIGHT')
#            bpy.ops.sequencer.cut(frame=aend, type='SOFT', side='RIGHT')
#        
#        bpy.ops.sequencer.select_all(action='DESELECT')
#        chan=new.channel
#        for s in scene.sequence_editor.sequences_all:
#            st=s.frame_start+s.frame_offset_start
#            en=sta+s.frame_final_duration
#            if s.channel==chan:
#                if st==rstart or en==rstart+lgt:
#                    s.select=True
#            if active_item.audio_channels!=0 and chka==1:
#                if s.channel==new_sound.channel:
#                    if st==rastart or en==rastart+lgt:
#                        s.select=True
#        bpy.ops.sequencer.delete()
#        
#        
#        #new.channel=propscene.active_audio_channel
#        if chk==1 or chka==1:
#            bpy.context.scene.sequence_editor.active_strip = new
#        
#        return {'FINISHED'}
    
    
#Splice on Timeline
class BleditSpliceOnTimeline(bpy.types.Operator):
    bl_idname = "bledit.splice_on_timeline"
    bl_label = "Splice on Timeline"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        chan_props=propscene.channel_properties
        active_bin=props.bin_list[props.active_bin_index]
        active=props.bin_list[props.active_bin_index].bin_content[active_bin.active_item_index]
        index=active_bin.active_item_index
        cf=bpy.context.scene.frame_current
        scene=bpy.context.scene
        addon_preferences = get_addon_preferences()
        
        u_in=propscene.use_in
        u_out=propscene.use_out
        inp=propscene.in_point
        outp=propscene.out_point
        
        #fct to create sequencer
        BleditCreateSequencer()
        
        if u_in==True and u_out==True and inp<outp:
            scene.frame_current=inp
            lgtIO=outp-scene.frame_current
            if active.type=="Image":
                lgt=addon_preferences.still_image_length*props.project_framerate
                if lgt>lgtIO:
                    lgt=lgtIO
            else:
                lgt=active.length[0].total_frames
                if lgt>lgtIO:
                    lgt=lgtIO
            
        elif u_in==True:
            scene.frame_current=inp
            if active.type=="Image":
                lgt=addon_preferences.still_image_length*props.project_framerate
            else:
                lgt=active.length[0].total_frames
                    
        elif u_out==True and scene.frame_current<outp:
            lgtIO=outp-scene.frame_current
            if active.type=="Image":
                lgt=addon_preferences.still_image_length*props.project_framerate
                if lgt>lgtIO:
                    lgt=lgtIO
            else:
                lgt=active.length[0].total_frames
                if lgt>lgtIO:
                    lgt=lgtIO
            
        else:
            if active.type=="Image":
                lgt=addon_preferences.still_image_length*props.project_framerate
            else:
                lgt=active.length[0].total_frames
                
        if active.type=='Audio':
            channel=propscene.active_audio_channel
        else:
            channel=propscene.active_video_channel
        
        #bpy.ops.sequencer.refresh_all()
        bpy.ops.sequencer.select_all(action='DESELECT')
        for s in scene.sequence_editor.sequences_all:
            st=s.frame_start+s.frame_offset_start
            en=st+s.frame_final_duration
            if s.channel==channel or chan_props[s.channel-1].sync_lock==True:
                if st<scene.frame_current and en>scene.frame_current:
                    #tocut.append(s)
                    s.select=True
                    #bpy.ops.sequencer.cut(frame=scene.frame_current, type='SOFT', side='LEFT')
            elif active.type=='Video' and active.audio_channels!=0:
                if s.channel==propscene.active_audio_channel:
                    if st<scene.frame_current and en>scene.frame_current:
                        #tocut.append(s)
                        s.select=True
                        #bpy.ops.sequencer.cut(frame=scene.frame_current, type='SOFT', side='LEFT')
        bpy.ops.sequencer.cut(frame=scene.frame_current, type='SOFT', side='LEFT')

        #bpy.ops.sequencer.refresh_all()
        bpy.ops.sequencer.select_all(action='DESELECT')
        for s in scene.sequence_editor.sequences_all:
            st=s.frame_start+s.frame_offset_start
            en=st+s.frame_final_duration
            if s.channel==channel or chan_props[s.channel-1].sync_lock==True:
                if st>=scene.frame_current:
                    s.select=True
            elif active.type=='Video' and active.audio_channels!=0:
                if s.channel==propscene.active_audio_channel:
                    if st>=scene.frame_current:
                        s.select=True
   
        bpy.ops.transform.seq_slide(value=(lgt, 0))

        #new strip
        bpy.ops.sequencer.select_all(action='DESELECT')
        if active.type=="Image":
            new=bpy.context.scene.sequence_editor.sequences.new_image(active.name, active.path, channel, scene.frame_current)
            new.frame_final_duration=lgt
            new.channel=channel
        elif active.type=="Video":
            new=bpy.context.scene.sequence_editor.sequences.new_movie(active.name, active.path, channel, scene.frame_current)
            new.frame_final_duration=lgt
            new.channel=channel
            if active.audio_channels!=0:
                new_sound=bpy.context.scene.sequence_editor.sequences.new_sound(active.name, active.path, propscene.active_audio_channel, scene.frame_current)
                new_sound.frame_final_duration=lgt
                new_sound.channel=propscene.active_audio_channel
        elif active.type=="Audio":
            new=bpy.context.scene.sequence_editor.sequences.new_sound(active.name, active.path, channel, scene.frame_current)
            new.frame_final_duration=lgt
            new.channel=channel
        elif active.type=="Image Sequence":
            new=bpy.context.scene.sequence_editor.sequences.new_image(active.name, active.path, channel, scene.frame_current)
            #add element
            ct=0
            for file in os.listdir(os.path.split(active.path)[0]):
                if active.name in file and ct<lgt:
                    new.elements.append(file)
                    ct+=1
                elif ct==lgt:
                    break
            new.frame_final_duration=lgt
            new.channel=channel

        bpy.context.scene.sequence_editor.active_strip = new

        return {'FINISHED'}
    
#Clear In 
class BleditClearIn(bpy.types.Operator):
    bl_idname = "bledit.clear_in"
    bl_label = "Clear In Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.use_in==True
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.use_in=False
        if bpy.context.scene.use_preview_range == False:
            propscene.in_point=bpy.context.scene.frame_start
        else:
            propscene.in_point=bpy.context.scene.frame_preview_start
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        print("Blender Edit --- In Point Cleared")
            
        return {'FINISHED'}

#Clear Out 
class BleditClearOut(bpy.types.Operator):
    bl_idname = "bledit.clear_out"
    bl_label = "Clear Out Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.use_out==True
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.use_out=False
        if bpy.context.scene.use_preview_range == False:
            propscene.out_point=bpy.context.scene.frame_end
        else:
            propscene.out_point=bpy.context.scene.frame_preview_end
            
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        print("Blender Edit --- Out Point Cleared")
            
        return {'FINISHED'}
    
#Clear In Out 
class BleditClearInOut(bpy.types.Operator):
    bl_idname = "bledit.clear_in_out"
    bl_label = "Clear In and Out Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.use_in==True or propscene.use_out==True
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.use_in=False
        propscene.use_out=False
        if bpy.context.scene.use_preview_range == False:
            propscene.in_point=bpy.context.scene.frame_start
            propscene.out_point=bpy.context.scene.frame_end
        else:
            propscene.out_point=bpy.context.scene.frame_preview_start
            propscene.out_point=bpy.context.scene.frame_preview_end
            
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        print("Blender Edit --- Out Point Cleared")
            
        return {'FINISHED'}

#Set in 
class BleditSetIn(bpy.types.Operator):
    bl_idname = "bledit.set_in"
    bl_label = "Set In Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.use_in=True
        propscene.in_point=bpy.context.scene.frame_current
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        print("Blender Edit --- In Point Set")
            
        return {'FINISHED'}
    
#Set out
class BleditSetOut(bpy.types.Operator):
    bl_idname = "bledit.set_out"
    bl_label = "Set Out Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.use_out=True
        propscene.out_point=bpy.context.scene.frame_current
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()

        print("Blender Edit --- Out Point Set")
            
        return {'FINISHED'}

#Go to In
class BleditGotoIn(bpy.types.Operator):
    bl_idname = "bledit.goto_in"
    bl_label = "Go to In Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.use_in==True and propscene.in_point!=bpy.context.scene.frame_current
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        bpy.context.scene.frame_current=propscene.in_point
            
        return {'FINISHED'}

#Go to Out
class BleditGotoOut(bpy.types.Operator):
    bl_idname = "bledit.goto_out"
    bl_label = "Go to Out Point"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.use_out==True and propscene.out_point!=bpy.context.scene.frame_current
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        bpy.context.scene.frame_current=propscene.out_point
            
        return {'FINISHED'}
    
#video channel +1
class BleditNextVideoChannel(bpy.types.Operator):
    bl_idname = "bledit.next_video_channel"
    bl_label = "Next Active Video Channel"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.active_video_channel!=32
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.active_video_channel+=1
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {'FINISHED'}
    
#video channel -1
class BleditPreviousVideoChannel(bpy.types.Operator):
    bl_idname = "bledit.previous_video_channel"
    bl_label = "Previous Active Video Channel"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.active_video_channel!=1
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.active_video_channel-=1
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {'FINISHED'}
    
#audio channel +1
class BleditNextAudioChannel(bpy.types.Operator):
    bl_idname = "bledit.next_audio_channel"
    bl_label = "Next Active Audio Channel"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.active_audio_channel!=32
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.active_audio_channel+=1
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {'FINISHED'}

#audio channel -1
class BleditPreviousAudioChannel(bpy.types.Operator):
    bl_idname = "bledit.previous_audio_channel"
    bl_label = "Previous Active Audio Channel"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        return propscene.active_audio_channel!=1
    
    def execute(self, context):
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        propscene.active_audio_channel-=1
        
        for a in bpy.context.screen.areas:
            a.tag_redraw()
            
        return {'FINISHED'}

#create sequencer if doesn't exist
def BleditCreateSequencer(): 
    scene = bpy.context.scene 
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    return {'FINISHED'}

    
#test GUI
class BleditTestUI(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Blender Edit"
    bl_label = "Bin"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.space_data.view_type=='SEQUENCER'
        
    def draw(self, context):
        addon_preferences = get_addon_preferences()
        
        layout = self.layout
        if len(bpy.data.window_managers['WinMan'].blender_edit_properties)==0:
            layout.operator("bledit.initialize")
        else:
            props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
            propscene=bpy.context.scene.blender_edit_scene_properties[0]
            box=layout.box()
            row=box.row()
            row.label(text='', icon='SCRIPTWIN')
            row.operator("bleding.project_settings_menu")
            row.prop(props, "project_path", text='',expand=False)
            if props.running_autosave==False:
                row.operator("bledit.auto_save", text='Start Auto Save',icon='TIME')
            else:
                row.label("Auto Save running")
            row.operator("bledit.save_all_bins")
            
            box=layout.box()
            row=box.row(align=True)
            row.operator('bledit.set_in', icon='TRIA_RIGHT_BAR', text='In')
            row.operator('bledit.set_out', icon='TRIA_LEFT_BAR', text='Out')
            row.separator()
            row.operator('bledit.clear_in', icon='LOOP_FORWARDS', text='Clear In')
            row.operator('bledit.clear_out', icon='LOOP_BACK', text='Clear Out')
            row.operator('bledit.clear_in_out', text='Clear In-Out')
            row.separator()
            row.operator('bledit.goto_in', icon='TRIA_RIGHT', text='Go to In')
            row.operator('bledit.goto_out', icon='TRIA_LEFT', text='Go to Out')
            row=box.row(align=True)
            row.operator("bledit.channel_details", text='Channels', icon='SEQ_SEQUENCER')
            row.separator()
            row.prop(propscene, "active_video_channel", text='Video Channel')
            row.prop(propscene, "active_audio_channel", text='Audio Channel')
            
            split=layout.split()
            col1=split.column()
            box=col1.box()
            row=box.row(align=True)
            row.label("BIN")
            if len(props.bin_list)==0:
                row.operator("bledit.open_bin", icon="FILE_FOLDER")
                row.operator("bledit.create_bin", icon='ZOOMIN')
            else:
                active=props.bin_list[props.active_bin_index]
                row.operator("bledit.open_bin", text="Import", icon="FILE_FOLDER")
                row.separator()
                row.operator("bledit.create_bin", text='Create', icon='ZOOMIN')
                row.operator("bledit.bin_actions", icon='ZOOMOUT', text="Suppress").action = 'SUPPRESS'
                row.separator()
                row.prop(active, "open", icon='FILE_TICK')
                row=box.row()
                row.template_list("BleditBinList", "", props, "bin_list", props, "active_bin_index", rows=7)
                col=row.column(align=True)
                col.separator()
                col.operator("bledit.bin_actions", icon='TRIA_UP', text="").action = 'UP'
                col.operator("bledit.bin_actions", icon='TRIA_DOWN', text="").action = 'DOWN'
                col.separator()
                col.operator("bledit.bin_inspector", text='', icon='VIEWZOOM')
                col.operator("bledit.save_active_bin", text='', icon='DISK_DRIVE')
                col2=split.column()
                box=col2.box()
                row=box.row(align=True)
                if active.lock==True:
                    row.enabled=False
                row.label('Content')
                row.operator("bledit.refresh_bin", icon='FILE_REFRESH', text='Refresh')
                row.separator()
                row.operator("bledit.import_content", icon="ZOOMIN", text='Import')
                if len(active.bin_content)>0:
                    row.operator("bledit.content_actions", icon='ZOOMOUT', text="Suppress").action = 'SUPPRESS'
                    row.separator()
                    row.operator("bledit.content_actions", icon='CHECKBOX_HLT', text="Toggle").action = 'SELECT/DESELECT'
                    row=box.row()
                    row.template_list("BleditBinContentList", "", active, "bin_content", active, "active_item_index", rows=7)
                    col=row.column(align=True)
                    col.operator("bledit.content_actions", icon='TRIA_UP', text="").action = 'UP'
                    col.operator("bledit.content_actions", icon='TRIA_DOWN', text="").action = 'DOWN'
                    col.separator()
                    col.operator("bledit.content_inspector", text="", icon='VIEWZOOM')
                    col.operator("bledit.comment_inspector", text="", icon='TEXT')
                    col.menu('Bledit_Copy_menu', text='', icon='GHOST')
                    active_item=active.bin_content[active.active_item_index]
                    row=layout.row(align=True)
                    row.operator("bledit.overwrite_on_timeline", icon='REC')
                    row.operator("bledit.splice_on_timeline", icon='KEYTYPE_MOVING_HOLD_VEC')
#                    row.operator("bledit.replace_on_timeline")
#                    col=box.column(align=True)
#                    row=col.row(align=True)
#                    row.label('Start')
#                    row.prop(active_item.start[0], "hours", text='')
#                    row.prop(active_item.start[0], "minutes", text='')
#                    row.prop(active_item.start[0], "seconds", text='')
#                    row.prop(active_item.start[0], "frames", text='')
#                    row=col.row(align=True)
#                    row.label('End')
#                    row.prop(active_item.end[0], "hours", text='')
#                    row.prop(active_item.end[0], "minutes", text='')
#                    row.prop(active_item.end[0], "seconds", text='')
#                    row.prop(active_item.end[0], "frames", text='')


class BleditSequencerUI:
    
    def __init__(self):
        self.handle = bpy.types.SpaceSequenceEditor.draw_handler_add(
                   self.draw_callback_px,(),
                   'WINDOW', 'POST_PIXEL')

    def draw_callback_px(self):
        if len(bpy.data.window_managers['WinMan'].blender_edit_properties)!=0 and len(bpy.context.scene.blender_edit_scene_properties)!=0:
            context=bpy.context
            addon_preferences = get_addon_preferences()
            region = context.region
            props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
            propscene=bpy.context.scene.blender_edit_scene_properties[0]
            vid=propscene.active_video_channel
            aud=propscene.active_audio_channel
            offset=addon_preferences.channel_UI_offset
            cf=bpy.context.scene.frame_current
            col_off=0.7
            
            wh=[0.2,0.2,0.2,0.9]
            bl=[0.9,0.9,0.9,1]
            vidcolor=addon_preferences.channel_UI_Vcol
            if vidcolor[0]+vidcolor[1]+vidcolor[2]>1.5:
                vidtextcol=[0, 0, 0, 1]
            else:
                vidtextcol=[1, 1, 1, 1]
            audcolor=addon_preferences.channel_UI_Acol
            if audcolor[0]+audcolor[1]+audcolor[2]>1.5:
                audtextcol=[0, 0, 0, 1]
            else:
                audtextcol=[1, 1, 1, 1]
            xA=17.1+offset
            xA2=140+offset
            
            font_id = 0
            if propscene.use_in==True or propscene.use_out==True:
                #In Out
                xIn = propscene.in_point
                y = 0
                xIn, y = region.view2d.view_to_region(xIn, y, clip=False)
                xOut = propscene.out_point
                y2 = 100
                xOut, y2 = region.view2d.view_to_region(xOut, y2, clip=False)
                yTxt=35
                w=xOut-xIn
                h=y2-y
            if propscene.use_in==True and propscene.use_out==True and propscene.in_point<=propscene.out_point:
                #In Out Zone
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glColor4f(*[1,1,1,0.1])
                bgl.glBegin(bgl.GL_QUADS)
                bgl.glVertex2f(xIn + w, y + h)
                bgl.glVertex2f(xIn, y + h)
                bgl.glVertex2f(xIn, y)
                bgl.glVertex2f(xIn + w, y)
                bgl.glEnd()
            #IN
            bgl.glColor4f(*[1,1,1,1])
            bgl.glLineWidth(2)
            if propscene.use_in==True:
                if cf!=propscene.in_point:
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    bgl.glVertex2f(xIn, y)
                    bgl.glVertex2f(xIn, y2)
                    bgl.glEnd()
                blf.position(font_id, xIn-20, yTxt, 0)
                blf.size(font_id, 13, 72)
                blf.draw(font_id, 'In')
            #OUT
            if propscene.use_out==True:
                if cf!=propscene.out_point:
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    bgl.glVertex2f(xOut, y)
                    bgl.glVertex2f(xOut, y2)
                    bgl.glEnd()
                blf.position(font_id, xOut+5, yTxt, 0)
                blf.size(font_id, 13, 72)
                blf.draw(font_id, 'Out')
            
            #vid
            x = context.scene.frame_current-0.5
            y = vid
            x, y = region.view2d.view_to_region(x, y, clip=False)
            x2=context.scene.frame_current+0.5
            y2 = vid+1
            x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
            x=xA
            x2=xA2
            w=x2-x
            h=y2-y
            
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(*vidcolor)
            bgl.glLineWidth(1)
            bgl.glBegin(bgl.GL_QUADS)
            bgl.glVertex2f(x + w, y + h)
            bgl.glVertex2f(x, y + h)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + w, y)
            bgl.glEnd()
            bgl.glColor4f(*bl)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x2, y)
            bgl.glEnd()
            # draw some text
            bgl.glColor4f(*vidtextcol)
            blf.position(font_id, x+5, y+2, 0)
            blf.size(font_id, 10, 72)
            blf.draw(font_id, "V")
            
            blf.position(font_id, x+20, y+2, 0)
            blf.size(font_id, 10, 72)
            if propscene.channel_properties[vid-1].sync_lock==True:
                blf.draw(font_id, "L")
            else:
                blf.draw(font_id, "U")
            

            #aud
            x = context.scene.frame_current-0.5
            y = aud
            x, y = region.view2d.view_to_region(x, y, clip=False)
            x2=context.scene.frame_current+0.5
            y2 = aud+1
            x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
            x=xA
            x2=xA2
            w=x2-x
            h=y2-y
            
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(*audcolor)
            bgl.glLineWidth(1)
            bgl.glBegin(bgl.GL_QUADS)
            bgl.glVertex2f(x + w, y + h)
            bgl.glVertex2f(x, y + h)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + w, y)
            bgl.glEnd()
            bgl.glColor4f(*bl)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x2, y)
            bgl.glEnd()
            # draw some text
            font_id = 0
            bgl.glColor4f(*audtextcol)
            blf.position(font_id, x+5, y+2, 0)
            blf.size(font_id, 10, 72)
            blf.draw(font_id, "A")
            
            blf.position(font_id, x+20, y+2, 0)
            blf.size(font_id, 10, 72)
            if propscene.channel_properties[aud-1].sync_lock==True:
                blf.draw(font_id, "L")
            else:
                blf.draw(font_id, "U")
            
            #draw channel numbers
            for n in range(1, 33):
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
                if n!=vid and n!=aud:
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glColor4f(*wh)
                    bgl.glLineWidth(1)
                    bgl.glBegin(bgl.GL_QUADS)
                    bgl.glVertex2f(x + w, y + h)
                    bgl.glVertex2f(x, y + h)
                    bgl.glVertex2f(x, y)
                    bgl.glVertex2f(x + w, y)
                    bgl.glEnd()
                    bgl.glColor4f(*bl)
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    bgl.glVertex2f(x, y)
                    bgl.glVertex2f(x2, y)
                    bgl.glEnd()
                    # draw some text
                    font_id = 0
                    bgl.glColor4f(*bl)
                    blf.position(font_id, x+5, y+3, 0)
                    blf.size(font_id, 10, 72)
                    blf.draw(font_id, str(n))
                    
                    blf.position(font_id, x+20, y+2, 0)
                    blf.size(font_id, 10, 72)
                    if propscene.channel_properties[n-1].sync_lock==True:
                        blf.draw(font_id, "L")
                    else:
                        blf.draw(font_id, "U")
                    #draw channel names
                    blf.position(font_id, x+35, y+2, 0)
                    blf.size(font_id, 10, 72)
                    blf.draw(font_id, str(propscene.channel_properties[n-1].name))
                else:
                    if n==vid:
                        bgl.glColor4f(*vidtextcol)
                        #draw channel names
                        blf.position(font_id, x+35, y+2, 0)
                        blf.size(font_id, 10, 72)
                        blf.draw(font_id, str(propscene.channel_properties[n-1].name))
                    else:
                        bgl.glColor4f(*audtextcol)
                        #draw channel names
                        blf.position(font_id, x+35, y+2, 0)
                        blf.size(font_id, 10, 72)
                        blf.draw(font_id, str(propscene.channel_properties[n-1].name))
                
            #lines
            x = context.scene.frame_current-0.5
            y = 1
            x, y = region.view2d.view_to_region(x, y, clip=False)
            x2=context.scene.frame_current+0.5
            y2 = 33
            x2, y2 = region.view2d.view_to_region(x2, y2, clip=False)
            x1=xA+30
            x2=xA+17
            x3=xA2
    #        bgl.glColor4f(*bl)
    #        bgl.glLineWidth(1)
    #        bgl.glBegin(bgl.GL_LINE_STRIP)
    #        bgl.glVertex2f(x1, y)
    #        bgl.glVertex2f(x1, y2)
    #        bgl.glEnd()
    #        bgl.glBegin(bgl.GL_LINE_STRIP)
    #        bgl.glVertex2f(x2, y)
    #        bgl.glVertex2f(x2, y2)
    #        bgl.glEnd()
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(x3, y)
            bgl.glVertex2f(x3, y2)
            bgl.glEnd()
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(xA, y2)
            bgl.glVertex2f(xA2, y2)
            bgl.glEnd()
        

    def remove_handle(self):
         bpy.types.SpaceSequenceEditor.draw_handler_remove(self.handle, 'WINDOW')

#Copy Menu
class BleditCopyContentMenu(bpy.types.Menu):
    bl_label = "Copy Selection To"
    bl_idname = "Bledit_Copy_menu"
    bl_description = "Copy selected items to other opened Bin"
    
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        layout = self.layout
        split=layout.split()
        col=split.column()
        col.label("Copy to")
        col.separator()
        if len(props.bin_list)!=0:
            index=-1
            for b in props.bin_list:
                row=col.row()
                index+=1
                op=row.operator('bledit.copy_content', text=b.name)
                op.index=index            
                if props.bin_list[index].open==False or index==props.active_bin_index:
                    row.enabled=False

        col=split.column()
        col.label("Move to")
        col.separator()
        if len(props.bin_list)!=0:
            index=-1
            for b in props.bin_list:
                row=col.row()
                index+=1
                op=row.operator('bledit.move_content', text=b.name)
                op.index=index            
                if props.bin_list[index].open==False or index==props.active_bin_index:
                    row.enabled=False
                    
                    
#persistent menu for project settings
class BleditProjectSettings(bpy.types.Operator):
    bl_idname = "bleding.project_settings_menu"
    bl_label = "Project Settings"
    bl_options = {'REGISTER', 'UNDO'}

#    @classmethod
#    def poll(cls, context):
#        return (context.material or context.object) and CyclesButtonsPanel.poll(context)
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        ob = context.object
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=100)
    def check(self, context):
        return True
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        layout = self.layout
        layout.label("Project Settings")
        layout.prop(props, "project_framerate", text='Project Framerate')
        layout.label("Project Index : "+str(props.project_idx))
        #layout.prop(props, "still_image_length", text='Image Duration')
        #layout.label("Open Project Folder")
        #layout.label("Open Backup Bin Folder")
        
#persistent menu for bin inspector
class BleditBinInspector(bpy.types.Operator):
    bl_idname = "bledit.bin_inspector"
    bl_label = "Bin Details"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
        except IndexError:
            chk=1
        return chk==0
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        ob = context.object
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=100)
    def check(self, context):
        return True
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        layout = self.layout
        layout.label("File : "+active_bin.path)
        layout.label("From Project : "+active_bin.origin)
        layout.label("Creation Date : "+active_bin.creation)
                
#persistent menu for content inspector
class BleditContentInspector(bpy.types.Operator):
    bl_idname = "bledit.content_inspector"
    bl_label = "Content Details"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
            active_item=active_bin.bin_content[active_bin.active_item_index]
        except IndexError:
            chk=1
        return chk==0
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        ob = context.object
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=100)
    def check(self, context):
        return True
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        
        layout = self.layout
        layout.label(active_item.name)
        row=layout.row()
        split=row.split()
        col=split.column(align=True)
        col.label("Length")
        col.label("Frames number")
        col.label("Path")
        col.label('Type')
        col.label("Framerate")
        col.label("Resolution")
        col.label("Codec")
        col.label("Color Depth")
        col.label("Color Space")
        col.label("Bitrate")
        col.separator()
        col.label("Audio Channels")
        col.label("Audio Layout")
        col.label("Audio Sample Rate")
        col.label("Audio Codec")
        
        col=split.column(align=True)
        col.label(str(active_item.length[0].hours).zfill(2)+":"+str(active_item.length[0].minutes).zfill(2)+":"+str(active_item.length[0].seconds).zfill(2)+":"+str(active_item.length[0].frames).zfill(2))
        col.label(str(active_item.length[0].total_frames))
        col.label(active_item.path)
        col.label(active_item.type)
        col.label(str(active_item.framerate))
        col.label(str(active_item.x_resolution)+" x "+str(active_item.y_resolution))
        col.label(str(active_item.codec))
        col.label(str(active_item.colordepth))
        col.label(str(active_item.color_space))
        col.label(str(active_item.bitrate))
        col.separator()
        col.label(str(active_item.audio_channels))
        col.label(str(active_item.audio_layout))
        col.label(str(active_item.audio_sample_rate))
        col.label(str(active_item.audio_codec))
        
#persistent menu for comment inspector
class BleditCommentInspector(bpy.types.Operator):
    bl_idname = "bledit.comment_inspector"
    bl_label = "Comment Details"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        chk=0
        try:
            active_bin=props.bin_list[props.active_bin_index]
            active_item=active_bin.bin_content[active_bin.active_item_index]
        except IndexError:
            chk=1
        return chk==0
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        ob = context.object
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
    def check(self, context):
        return True
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        active_bin=props.bin_list[props.active_bin_index]
        active_item=active_bin.bin_content[active_bin.active_item_index]
        
        layout = self.layout
        layout.label("Comment Section")
        row=layout.row()
        row.template_list("BleditCommentList", "", active_item, "comment", active_item, "active_comment_index", rows=5)
        col=row.column(align=True)
        col.operator("bledit.comment_actions", icon='ZOOMOUT', text="").action = 'SUPPRESS'
        col.separator()
        col.operator("bledit.comment_actions", icon='TRIA_UP', text="").action = 'UP'
        col.operator("bledit.comment_actions", icon='TRIA_DOWN', text="").action = 'DOWN'
        layout.prop(props, "temporary_comment", text='')
        layout.prop(props, "temporary_comment_author", text='Author')
        layout.operator("bledit.add_comment")
        
#persistent menu for chanel inspector
class BleditChannelInspector(bpy.types.Operator):
    bl_idname = "bledit.channel_details"
    bl_label = "Channel Details"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        ob = context.object
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=100)
    def check(self, context):
        return True
    def draw(self, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        channel=propscene.channel_properties
        layout = self.layout
        col=layout.column(align=True)
        for c in channel:
            row=col.row(align=True)
            row.label("Channel "+str(c.channel_number))
            row.separator()
            row.prop(c, "name", text='')
            row.separator()
            row.prop(c, "sync_lock", text='Sync Lock')


#Initialize operator
class BleditInitialize(bpy.types.Operator):
    bl_idname = "bledit.initialize"
    bl_label = "Initialize Blender Edit"
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].blender_edit_properties)==0 and bpy.data.is_saved==True
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        database=addon_preferences.data_base_folder
        bledit_props=bpy.data.window_managers['WinMan'].blender_edit_properties
        propscene=bpy.context.scene.blender_edit_scene_properties
        
        idx=0
        
        #create pref folder
        if os.path.isdir(database)==False:
            os.makedirs(database)
            
        for s in bpy.data.scenes:
            try:
                idx=s.blender_edit_scene_properties[0].project_idx
            except IndexError:
                print("Blender Edit --- Searching for Project in Database")
        
        if len(propscene)==0:
            propscene.add()
            #create channels
            for n in range(1, 33):
                new=propscene[0].channel_properties.add()
                new.name="channel_"+str(n).zfill(2)
                new.channel_number=n
        if len(bledit_props)==0:
            bledit_props.add()
        
        #load existing project
        if idx!=0:
            file=''
            for f in os.listdir(database):
                if int(f.split(".")[0])==idx:
                    file=os.path.join(database, f)
            lines=[]
            if file!='':
                with open(file, 'r', newline='') as csvfile:
                    line = csv.reader(csvfile, delimiter='\n')
                    for l in line:
                        l1=str(l).replace("[", "")
                        l2=l1.replace("]", "")
                        l3=l2.replace("'", "")
                        l4=l3.replace('"', "")
                        lines.append(l4)
                bledit_props[0].project_path=os.path.abspath(lines[0])
                bledit_props[0].framerate=int(lines[1])
                print("Blender Edit --- Project "+str(idx)+" loaded")
            else:
                blendname=os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0]
                print("Blender Edit --- Project "+str(idx)+" doesn't exist")
                propscene[0].project_idx=idx
                newf=os.path.join(database, str(idx))
                nfile = open(newf, "w")
                nfile.write(os.path.join(bpy.path.abspath("//"), "blender_edit_"+blendname)+"\n")
                nfile.write(str(addon_preferences.default_framerate)+"\n")
                nfile.close()
                bledit_props[0].project_path=os.path.join(bpy.path.abspath("//"), "blender_edit_"+blendname)
                bledit_props[0].framerate=addon_preferences.default_framerate
                print("Blender Edit --- Project "+str(idx)+" created")
                
            #load project path bins
            if os.path.isdir(bledit_props[0].project_path)==True:
                bpy.ops.bledit.import_project_bins()
        
        else:    
            blendname=os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0]
            #create new one
            idx=random.randint(00000, 99999)
            print("Blender Edit --- Project not found")
            print("Blender Edit --- Creation of New Project " + str(idx))
            propscene[0].project_idx=idx
            newf=os.path.join(database, str(idx))
            nfile = open(newf, "w")
            nfile.write(os.path.join(bpy.path.abspath("//"), "blender_edit_"+blendname)+"\n")
            nfile.write(str(addon_preferences.default_framerate)+"\n")
            nfile.close()
            
            #main prop
            bledit_props[0].project_path=os.path.join(bpy.path.abspath("//"), "blender_edit_"+blendname)
            bledit_props[0].project_framerate=addon_preferences.default_framerate
        
                
        bledit_props[0].project_idx=idx
        
        print("Blender Edit --- Initialized")
        
        bpy.ops.wm.save_mainfile()
        
        #start auto save modal
        bpy.ops.bledit.auto_save()
        
        return {'FINISHED'}
    
#Import Project Bins
class BleditImportPojectBins(bpy.types.Operator):
    bl_idname = "bledit.import_project_bins"
    bl_label = "Import Poject Bins"
    
    files = bpy.props.CollectionProperty(name='files', type=bpy.types.OperatorFileListElement)
    directory = bpy.props.StringProperty(subtype='DIR_PATH', default="")
    
    @classmethod
    def poll(cls, context):
        props=bpy.data.window_managers['WinMan'].blender_edit_properties
        return len(props)!=0 and bpy.data.is_saved==True and props[0].project_path!=''
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        database=addon_preferences.data_base_folder
        props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
        propscene=bpy.context.scene.blender_edit_scene_properties[0]
        project_path=props.project_path
        
        self.directory=project_path
        
        files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f)) and ".bb" in f]
        
        for f in files:
            new=self.files.add()
            new.name=f
            
        bledit_read_bin(self.files, self.directory, context)
        
        print("Blender Edit --- Project Bins loaded")
        
        return {'FINISHED'}
    
#update database
def bledit_update_database(self, context):
    addon_preferences = get_addon_preferences()
    database=addon_preferences.data_base_folder
    idx=0
    bledit_props=bpy.data.window_managers['WinMan'].blender_edit_properties
    propscene=bpy.context.scene.blender_edit_scene_properties
    
    for s in bpy.data.scenes:
        try:
            idx=s.blender_edit_scene_properties[0].project_idx
        except IndexError:
            print("Blender Edit --- Searching for Project in Database")
    if idx!=0:
        file=os.path.join(database, str(idx))
        os.remove(file)
        nfile = open(file, "w")
        nfile.write(bledit_props[0].project_path+"\n")
        nfile.write(str(bledit_props[0].project_framerate)+"\n")
        nfile.close()
        print("Blender Edit --- Project updated in Database")
    
    
                    
#######################################################################
### collections ###
#######################################################################      

class BlenderEditTimecodeProperties(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    hours = bpy.props.IntProperty(min=0, max=99, update=bledit_update_modified_bin)
    minutes = bpy.props.IntProperty(min=0, max=59, update=bledit_update_modified_bin)
    seconds = bpy.props.IntProperty(min=0, max=59, update=bledit_update_modified_bin)
    frames = bpy.props.IntProperty(min=0, max=24, update=bledit_update_modified_bin)
    total_frames = bpy.props.IntProperty(min=1, update=bledit_update_modified_bin)
    
class BlenderEditCustomComment(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    creation = bpy.props.StringProperty()
    author = bpy.props.StringProperty()
    
class BlenderChannelProperties(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    channel_number = bpy.props.IntProperty(min=1, max=32)
    sync_lock = bpy.props.BoolProperty(default=False)

class BlenderEditBinContent(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    path = bpy.props.StringProperty(subtype="FILE_PATH")
    type = bpy.props.EnumProperty(items=(("Image", "Image",'', 'FILE_IMAGE', 0),
            ("Video", "Video",'', 'FILE_MOVIE', 1),
            ("Audio", "Audio",'', 'FILE_SOUND', 2),
            ("Image Sequence", "Image Sequence",'', 'IMAGE_COL', 3),
            ("Timeline", "Timeline",'', 'SEQ_SEQUENCER', 4),
            ),
            name='Type')
    length = bpy.props.CollectionProperty(type=BlenderEditTimecodeProperties)
    start = bpy.props.CollectionProperty(type=BlenderEditTimecodeProperties)
    end = bpy.props.CollectionProperty(type=BlenderEditTimecodeProperties)
    idx = bpy.props.IntProperty()
    active_comment_index = bpy.props.IntProperty(min=0, default=0)  
    comment = bpy.props.CollectionProperty(type=BlenderEditCustomComment)
    x_resolution = bpy.props.IntProperty(min=0)
    y_resolution = bpy.props.IntProperty(min=0)
    framerate = bpy.props.IntProperty(min=0)
    codec = bpy.props.StringProperty(default="none")
    color_space = bpy.props.StringProperty(default="none")
    bitrate = bpy.props.IntProperty(default=0)
    colordepth = bpy.props.IntProperty(default=0)
    audio_channels = bpy.props.IntProperty(default=0)
    audio_sample_rate = bpy.props.IntProperty(default=0)
    audio_layout = bpy.props.EnumProperty(items=(("none", "None",''),
            ("stereo", "Stereo",''),
            ("unknown", "Unknown",''),
            ("mono", "Mono",'')),
            name='Audio Layout')
    audio_codec = bpy.props.StringProperty(default="none")
    selected = bpy.props.BoolProperty(default=False)
    
class BlenderEditBinList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default = "new_bin", update=bledit_update_name_bin)
    idx = bpy.props.IntProperty()
    path = bpy.props.StringProperty(subtype="FILE_PATH")
    lock = bpy.props.BoolProperty(default=False)
    open = bpy.props.BoolProperty(default=False, update=bledit_update_open_close)
    origin = bpy.props.StringProperty()
    creation = bpy.props.StringProperty()
    modification = bpy.props.FloatProperty(subtype="TIME")
    bin_content = bpy.props.CollectionProperty(type=BlenderEditBinContent)
    active_item_index = bpy.props.IntProperty(min=0, default=0, update=bledit_update_item_selection)
    modified = bpy.props.BoolProperty(default=False)
        
class BlenderEditProperties(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    project_path = bpy.props.StringProperty(subtype="DIR_PATH", update=bledit_update_database)
    project_framerate = bpy.props.IntProperty(min=1, default=25, update=bledit_update_database)
    bin_list = bpy.props.CollectionProperty(type=BlenderEditBinList)
    active_bin_index = bpy.props.IntProperty(min=0, default=0)
    auto_detect_image_sequence = bpy.props.BoolProperty(default=True)
    temporary_comment = bpy.props.StringProperty(default="")
    temporary_comment_author = bpy.props.StringProperty(default="")
    minimum_image_sequence = bpy.props.IntProperty(min=2, default=3)
    running_autosave = bpy.props.BoolProperty(default=False)
    project_idx = bpy.props.IntProperty()
    #ffprobe_path = bpy.props.StringProperty(subtype="FILE_PATH", default="C:\\Program Files\\ffmpeg-3.1.4-win64-static\\bin\\ffprobe.exe")
    #maximum_old_bin = bpy.props.IntProperty(min=2, max=250, default=10)
    #autosave_frequency = bpy.props.IntProperty(min=1, max=120, default=10)
    #still_image_length = bpy.props.IntProperty(min=1, max=120, default=3)
    #active_video_channel = bpy.props.IntProperty(min=1, max=32, default=2)
    #active_audio_channel = bpy.props.IntProperty(min=1, max=32, default=1)
    #channel_UI_offset = bpy.props.IntProperty(min=0, default=0)
    #channel_UI_Vcol = bpy.props.FloatVectorProperty(size=4, min=0.0, max=1.0, default=[0.4, 0.4, 1.0, 0.9], subtype='COLOR')
    #channel_UI_Acol = bpy.props.FloatVectorProperty(size=4, min=0.0, max=1.0,default=[0.5, 1.0, 1.0, 0.9], subtype='COLOR')
    #channel_properties = bpy.props.CollectionProperty(type=BlenderChannelProperties)
    
class BlenderEditSceneProperties(bpy.types.PropertyGroup):
    '''name = StringProperty(default = "Slot")'''
    project_idx = bpy.props.IntProperty()
    active_video_channel = bpy.props.IntProperty(min=1, max=32, default=2)
    active_audio_channel = bpy.props.IntProperty(min=1, max=32, default=1)
    channel_properties = bpy.props.CollectionProperty(type=BlenderChannelProperties)
    in_point = bpy.props.IntProperty(min=0, default=1)
    out_point = bpy.props.IntProperty(min=1, default=10)
    use_in = bpy.props.BoolProperty(default=False)
    use_out = bpy.props.BoolProperty(default=False)
    
#######################################################################
### handler ###
#######################################################################

#handler  
@persistent
def handler_change_blend(context):
    props=bpy.data.window_managers['WinMan'].blender_edit_properties[0]
    project_path=props.project_path
    bin_list=props.bin_list
    #close all bins
    ct=-1
    for b in bin_list:
        ct+=1
        if b.open==True:
            props.active_bin_index=ct
            b.open=False
            print("Blender Edit --- Closing "+b.name)
    if os.path.isdir(project_path)==True:
        #clean old blck
        bins = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f)) and ".bb" in f]
        locks = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f)) and ".blck" in f]
        for l in locks:
            chk=0
            for b in bins:
                if os.path.splitext(b)[0]==os.path.splitext(l)[0]:
                    chk=1
            if chk==0:
                os.remove(os.path.join(project_path, l))
                print("Blender Edit --- Cleaning " + l)
    
    
#######################################################################
### reg/unreg ###
#######################################################################
widgets = {}

def register():
    widgets["SequencerUI"] = BleditSequencerUI()
    
    bpy.utils.register_class(BLeditAddonPrefs)
    
    bpy.utils.register_class(BleditCreateBin)
    bpy.utils.register_class(BleditOpenBin)
    bpy.utils.register_class(BleditRefreshBin)
    bpy.utils.register_class(BleditImportContent)
    bpy.utils.register_class(BleditAddComment)
    bpy.utils.register_class(BleditSaveActiveBin)
    bpy.utils.register_class(BleditSaveAllBins)
    bpy.utils.register_class(BleditModalAutoSave)
    bpy.utils.register_class(BleditCopyContent)
    bpy.utils.register_class(BleditMoveContent)
    
    bpy.utils.register_class(BleditBinActions)
    bpy.utils.register_class(BleditContentActions)
    bpy.utils.register_class(BleditCommentActions)
    
    bpy.utils.register_class(BleditBinList)
    bpy.utils.register_class(BleditBinContentList)
    bpy.utils.register_class(BleditCommentList)
    
    bpy.utils.register_class(BleditOverwriteOnTimeline)
#    bpy.utils.register_class(BleditReplaceOnTimeline)
    bpy.utils.register_class(BleditSpliceOnTimeline)
    
    bpy.utils.register_class(BleditClearIn)
    bpy.utils.register_class(BleditClearOut)
    bpy.utils.register_class(BleditClearInOut)
    bpy.utils.register_class(BleditSetIn)
    bpy.utils.register_class(BleditSetOut)
    bpy.utils.register_class(BleditGotoIn)
    bpy.utils.register_class(BleditGotoOut)
    
    bpy.utils.register_class(BleditNextVideoChannel)
    bpy.utils.register_class(BleditPreviousVideoChannel)
    bpy.utils.register_class(BleditNextAudioChannel)
    bpy.utils.register_class(BleditPreviousAudioChannel)
    
    bpy.utils.register_class(BleditTestUI)
    bpy.utils.register_class(BleditCopyContentMenu)
    bpy.utils.register_class(BleditProjectSettings)
    bpy.utils.register_class(BleditBinInspector)
    bpy.utils.register_class(BleditContentInspector)
    bpy.utils.register_class(BleditCommentInspector)
    bpy.utils.register_class(BleditChannelInspector)
    
    bpy.utils.register_class(BleditInitialize)
    bpy.utils.register_class(BleditImportPojectBins)
    
    bpy.utils.register_class(BlenderEditTimecodeProperties)
    bpy.utils.register_class(BlenderEditCustomComment)
    bpy.utils.register_class(BlenderChannelProperties)
    bpy.utils.register_class(BlenderEditBinContent)      
    bpy.utils.register_class(BlenderEditBinList)
    bpy.utils.register_class(BlenderEditProperties)
    bpy.utils.register_class(BlenderEditSceneProperties)
    
    bpy.types.WindowManager.blender_edit_properties = \
        bpy.props.CollectionProperty(type=BlenderEditProperties)
        
    bpy.types.Scene.blender_edit_scene_properties = \
        bpy.props.CollectionProperty(type=BlenderEditSceneProperties)

    #bpy.types.INFO_MT_file_import.append(bledit_open_bin)
    
    bpy.app.handlers.load_pre.append(handler_change_blend)
                                
def unregister():
    for key, dc in widgets.items():
        dc.remove_handle()
    
    bpy.utils.unregister_class(BLeditAddonPrefs)
    
    bpy.utils.unregister_class(BleditCreateBin)
    bpy.utils.unregister_class(BleditOpenBin)
    bpy.utils.unregister_class(BleditRefreshBin)
    bpy.utils.unregister_class(BleditImportContent)
    bpy.utils.unregister_class(BleditAddComment)
    bpy.utils.unregister_class(BleditSaveActiveBin)
    bpy.utils.unregister_class(BleditSaveAllBins)
    bpy.utils.unregister_class(BleditModalAutoSave)
    bpy.utils.unregister_class(BleditCopyContent)
    bpy.utils.unregister_class(BleditMoveContent)
    
    bpy.utils.unregister_class(BleditBinActions)
    bpy.utils.unregister_class(BleditContentActions)
    bpy.utils.unregister_class(BleditCommentActions)
    
    bpy.utils.unregister_class(BleditBinList)
    bpy.utils.unregister_class(BleditBinContentList)
    bpy.utils.unregister_class(BleditCommentList)
    
    bpy.utils.unregister_class(BleditOverwriteOnTimeline)
#    bpy.utils.unregister_class(BleditReplaceOnTimeline)
    bpy.utils.unregister_class(BleditSpliceOnTimeline)
    
    bpy.utils.unregister_class(BleditClearIn)
    bpy.utils.unregister_class(BleditClearOut)
    bpy.utils.unregister_class(BleditClearInOut)
    bpy.utils.unregister_class(BleditSetIn)
    bpy.utils.unregister_class(BleditSetOut)
    bpy.utils.unregister_class(BleditGotoIn)
    bpy.utils.unregister_class(BleditGotoOut)
    
    bpy.utils.unregister_class(BleditTestUI)
    bpy.utils.unregister_class(BleditCopyContentMenu)
    bpy.utils.unregister_class(BleditProjectSettings)
    bpy.utils.unregister_class(BleditBinInspector)
    bpy.utils.unregister_class(BleditContentInspector)
    bpy.utils.unregister_class(BleditCommentInspector)
    bpy.utils.unregister_class(BleditChannelInspector)
    
    bpy.utils.unregister_class(BleditInitialize)
    bpy.utils.unregister_class(BleditImportPojectBins)
    
    bpy.utils.unregister_class(BlenderEditTimecodeProperties)
    bpy.utils.unregister_class(BlenderEditCustomComment)
    bpy.utils.unregister_class(BlenderChannelProperties)
    bpy.utils.unregister_class(BlenderEditBinContent)
    bpy.utils.unregister_class(BlenderEditBinList)
    bpy.utils.unregister_class(BlenderEditProperties)
        
    del bpy.types.WindowManager.blender_edit_properties
    del bpy.types.Scene.blender_edit_scene_properties

    #bpy.types.INFO_MT_file_import.remove(bledit_open_bin)
    
    
    bpy.app.handlers.load_pre.remove(handler_change_blend)
            
if __name__ == "__main__":
    register()