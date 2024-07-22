# utils.py

from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui

def collect_geo_objects():
    all_objects = cmds.ls(dag=True, long=True)
    geo_objects = [obj for obj in all_objects if obj.endswith('_GEO')]
    
    geo_dict = {}
    for obj in geo_objects:
        short_name = obj.split('|')[-1]
        parts = short_name.split(':')
        if len(parts) == 1:
            namespace = 'default'
            obj_name = parts[0]
        else:
            namespace = ':'.join(parts[:-1])
            obj_name = parts[-1]
        if namespace not in geo_dict:
            geo_dict[namespace] = []
        geo_dict[namespace].append(obj_name)
    
    return geo_dict

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
