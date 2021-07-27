
from .recent_db_manager import RecentDBManager
import os, sys
from stat import *
from .settings_manager import *

class LatestLister():
    
       

    def getList(self):
        recentDBManager = RecentDBManager()
        recentDBManager.merge()
        recentDBManager = RecentDBManager()
        files_list = []
        
        for entry in  recentDBManager.getMyRecentDBNotes():
            f={}
            f['isFile'] = True
            f['name'] = entry
            f['path'] = "/"+entry
            files_list.append(f)
            
        return files_list
