import bpy
import json
import os

from .preferences import get_addon_preferences
from .misc_functions import absolute_path

def create_clip_json(path, data):
    with open(path, "w") as write_file:
        json.dump(data, write_file)
        
def suppress_existing_file(filepath):
    deleted=False
    if os.path.isfile(filepath)==True:
        os.remove(filepath)
        deleted=True
    return deleted

def get_strip_filepath(strip):
    if strip.type=='MOVIE':
        fp=absolute_path(strip.filepath)
    elif strip.type=='IMAGE':
        name=strip.elements[0].filename
        fp=os.path.join(absolute_path(strip.directory), name)
    elif strip.type=='SOUND':
        fp=absolute_path(strip.sound.filepath)
    else:
        fp=''
    return fp

def get_strip_infos(strip):
    if strip.type=='MOVIE':
        fp=absolute_path(strip.filepath)
        name=os.path.basename(fp)
        length=strip.frame_duration
    elif strip.type=='IMAGE':
        name=strip.elements[0].filename
        fp=os.path.join(absolute_path(strip.directory), name)
        length=len(strip.elements)
    elif strip.type=='SOUND':
        fp=absolute_path(strip.sound.filepath)
        name=os.path.basename(fp)
        length=strip.frame_duration
    else:
        name=fp=length=''
    proxy=return_proxys_filepath(strip)

    return name, fp, length, proxy

#get and format strip infos only
def format_strip_infos(strip):
    name, fp, length, proxy=get_strip_infos(strip)
    proxy=return_proxys_filepath(strip)
    datas = {
        "infos": {
            "name": name,
            "filepath": fp,
            "length": length,
            "proxys": proxy
        },
        "markers": [
        ]
    }
    return datas
    

def format_markers_infos(strip, comment, frame, author):
    name, fp, length, proxy=get_strip_infos(strip)
    proxy=return_proxys_filepath(strip)
            
    datas = {
        "infos": {
            "name": name,
            "filepath": fp,
            "length": length,
            "proxys": proxy
        },
        "markers": [{
            "comment": comment,
            "frame": frame,
            "author": author
        }]
    }
    return datas

# update markers
def update_markers_from_temp(json):
    old=read_json(json)
    props=bpy.context.scene.blender_edit_scene_properties[0]
    datas = {
        "infos": {
            "name": old['infos']['name'],
            "filepath": old['infos']['filepath'],
            "length": old['infos']['length'],
            "proxys": old['infos']['proxys']
        },
        "markers": [
        ]
    }
    if len(props.tempcomment)!=0:
        for m in props.tempcomment:
            if m.to_clear==False:
                datas['markers'].append({"comment":m.name, "frame":m.frame, "author":m.author})
    return datas

#add marker
def add_marker_to_json(olddata, comment, frame, author):
    olddata['markers'].append({"comment":comment, "frame":frame, "author":author})
    return olddata

#read json
def read_json(filepath):
    with open(filepath, "r") as read_file:
        data = json.load(read_file)
    return data

# return strip proxy filepath
def return_proxys_filepath(strip):
    scn=bpy.context.scene
    proxy=""
    fp=get_strip_filepath(strip)
    if strip.use_proxy==True:
        if scn.sequence_editor.proxy_storage=='PROJECT':
            proxy=scn.sequence_editor.proxy_dir
        elif scn.sequence_editor.proxy_storage=='PER_STRIP':
            if strip.proxy.use_proxy_custom_file==False and strip.proxy.use_proxy_custom_directory==False:
                proxy=os.path.join(os.path.dirname(fp), 'BL_proxy')
            elif strip.proxy.use_proxy_custom_file==False and strip.proxy.use_proxy_custom_directory==True:
                proxy=absolute_path(strip.proxy.directory)
            elif strip.proxy.use_proxy_custom_file==True:
                proxy=absolute_path(strip.proxy.filepath)
    return proxy

#update proxies
def update_proxies(strip, old):
    datas = {
        "infos": {
            "name": old['infos']['name'],
            "filepath": old['infos']['filepath'],
            "length": old['infos']['length'],
            "proxys": return_proxys_filepath(strip)
        },
        "markers": old['markers']
        
    }
    return datas