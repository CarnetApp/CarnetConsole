import os, sys
from stat import *
from .settings_manager import *

class PathLister():
    def __init__(self, path):
        self.path = path
        if(not self.path.startswith('/')):
            self.path = "/" + self.path

    def getList(self):
        files = os.scandir(settingsManager.getNotePath()+self.path)
        files_list = []
        dir_list = []
        for entry in files:
            if(self.path == "/" and entry.name =="quickdoc"):
                continue
            f={}
            f['isFile'] = entry.is_file()
            f['name'] = entry.name
            f['path'] = self.path+entry.name
            if(f['isFile']):
                files_list.append(f)
            else:
                dir_list.append(f)
        dir_list.extend(files_list)
        return dir_list
