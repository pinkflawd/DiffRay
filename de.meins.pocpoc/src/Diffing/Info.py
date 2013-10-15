'''
Created on 13.10.2013

@author: Marion
'''

import re

class Info(object):
    '''
    classdocs
    '''

    # TODO: list one lib + its hits
    # search for libids
    # diff 2 libs based on their ids

    def __init__(self, database):
        if (database == "mssql"):
            import Database.MSSqlDB
            self.db = Database.MSSqlDB.MSSqlDB()
        else:
            import Database.SQLiteDB
            self.db = Database.SQLiteDB.SQLiteDB()
        
        
    def search_libs(self, libname):
        print "Here are the IDs that could identify the requested lib %s:" % libname
        ids = self.db.select_libids_byname(libname)
        for item in ids:
            print "Library ID %s for %s" % (item['id'], item['libname'])
            
    def diff_libs(self, w7lib, w8lib):
        
        cur_win7 = self.db.select_diff_win7(w7lib)
        res = cur_win7.fetchmany(1000)
         
        print "Function_Name;Pattern;Win7_Hits;Win8_Hits"
        
        while res:
            for item in res:
                fsplit = re.split('\(', item['funcname'], 1, 0)
                
                cur_win8 = self.db.select_diff_win8(w8lib,item['sigpattern'],fsplit[0])
                hitcount8 = cur_win8.fetchone()
                
                if hitcount8:
                    print "%s;%s;%s;%s" % (fsplit[0],item['sigpattern'],item['co'],hitcount8['co'])
                else:
                    print "%s;%s;%s;" % (fsplit[0],item['sigpattern'],item['co'])
        
            res = cur_win7.fetchmany(1000)

    def library_info(self,libid):
        
        cur_all = self.db.select_lib_all(libid)
        print "Libname;Functionname;Sigpattern;Line_Offset"
        for item in cur_all:
            print "%s;%s;%s;%s" % (item['libname'],item['funcname'],item['sigpattern'],item['line_offset'])

        