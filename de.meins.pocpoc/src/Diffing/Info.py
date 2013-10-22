'''
Created on 13.10.2013

@author: Marion
'''

import re

class Info(object):
    '''
    INFO CLASS
    
    does all the info gathering out of the database
    stupid name i know
    '''


    def __init__(self, database):
        if (database == "mssql"):
            import Database.MSSqlDB
            self.db = Database.MSSqlDB.MSSqlDB()
        else:
            import Database.SQLiteDB
            self.db = Database.SQLiteDB.SQLiteDB()
        
        
    def search_libs(self, libname):
        ids = self.db.select_libs_byname(libname)
        for item in ids:
            print "Library ID %s for %s with type %s and OS %s" % (item['id'], item['libname'], item['filetype'], item['os'])
    
    
    def search_libs_diffing(self, libname):
        cur = self.db.select_libs_byname(libname)
        ids = cur.fetchall()    # without fetch the rowcount is always -1
        wids = []
        
        # works only for Win7/Win8 diffing !!
        if cur.rowcount == 2:
            if (ids[0]['filetype'].lower() == ids[1]['filetype'].lower()):
                if (ids[0]['os'] != ids[1]['os']):
                    
                    if (ids[0]['os'] == 'Win7'):
                        wids.append(ids[0]['id'])
                    elif (ids[1]['os'] == 'Win7'):
                        wids.append(ids[1]['id'])
                    else:
                        return -1
                    
                    if (ids[0]['os'] == 'Win8'):
                        wids.append(ids[0]['id'])
                    elif (ids[1]['os'] == 'Win8'):
                        wids.append(ids[1]['id'])
                    else:
                        return -1
                    
                    return wids
                else:
                    return -1
            else:
                return -1
        else:
            return -1

    
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

        