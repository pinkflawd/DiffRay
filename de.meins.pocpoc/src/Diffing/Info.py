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
                        print "1"
                        return -1
                    
                    if (ids[0]['os'] == 'Win8'):
                        wids.append(ids[0]['id'])
                    elif (ids[1]['os'] == 'Win8'):
                        wids.append(ids[1]['id'])
                    else:
                        print "2"
                        return -1
                    
                    return wids
                else:
                    print "3"
                    return -1
            else:
                print "4"
                return -1
        else:
            print "5"
            return -1

    
    def diff_libs(self, w7lib, w8lib):
        
        cur_one = self.db.select_diff_one(w8lib)
        res = cur_one.fetchall()
         
        print "Function_Name;Pattern;Win8_Hits;Win7_Hits"

        for item in res:
            fsplit = re.split('\(', item['funcname'], 1, 0)
            
            cur_two = self.db.select_diff_two(w7lib,item['sigpattern'],fsplit[0])
            hitcount_two = cur_two.fetchone()
             
            if hitcount_two:
                print "%s;%s;%s;%s" % (fsplit[0],item['sigpattern'],item['co'],hitcount_two['co'])
            elif (self.db.select_function(fsplit[0], w7lib)):
                print "%s;%s;%s;0" % (fsplit[0],item['sigpattern'],item['co'])
            else:
                print "%s;%s;%s;func_non_existent" % (fsplit[0],item['sigpattern'],item['co'])

    def get_0oes(self, w7lib, w8lib):
        pass

    def library_info(self,libid):
        
        cur_all = self.db.select_lib_all(libid)
        print "Libname;Functionname;Sigpattern;Line_Offset"
        for item in cur_all:
            print "%s;%s;%s;%s" % (item['libname'],item['funcname'],item['sigpattern'],item['line_offset'])

        