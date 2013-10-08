'''
Created on 12.09.2013

@author: pinkflawd
'''

from Exceptions import ParameterError
import re


class Function(object):
    '''
    FUNCTION CLASS
    represents the functions of a library in the database
    '''


    def __init__(self, libid, funcname, linecount, database):
        
        #if u wish so, check libid if integer. but basically, not necessary     
        self.libid = libid
        
        if len(funcname) < 999:
            sanifname = re.sub('\'','', funcname,0)
            self.funcname = sanifname
        else:
            raise ParameterError, "A funcname for function object is too long, max 999 chars."
        
        if linecount < 2147483647: 
            self.linecount = linecount
        else:
            raise ParameterError, "Linecount exceeds int range - weiiird should never happen."
        
        # might throw exception - theres no throws keyword :/
        if (database == "mssql"):
            import Database.MSSqlDB
            self.db = Database.MSSqlDB.MSSqlDB()
        else:
            import Database.SQLiteDB
            self.db = Database.SQLiteDB
                
        self.db.insert_function(self.libid,self.funcname,self.linecount)
        self.id = self.db.select_funcid(self.libid,self.funcname,self.linecount)
        
        
    def set_linecount(self,linecount):
        self.db.set_linecount(linecount, self.id)
    
    def signature_found(self, libid, funcid, sigpattern, line_offset):
        self.db.insert_hit(libid, funcid, sigpattern, line_offset)

