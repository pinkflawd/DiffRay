'''
Created on 12.09.2013

@author: pinkflawd
'''

import Database.MSSqlDB
from Exceptions import ParameterError
import re


class Function(object):
    '''
    FUNCTION CLASS
    represents the functions of a library in the database
    '''


    def __init__(self, libid, funcname, linecount):
        
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
        # self.db = Database.MSSqlDB.MSSqlDB()
        self.db = Database.SQLiteDB.SQLiteDB()
        self.db.insert_function(self.libid,self.funcname,self.linecount)
        select_string = "select id from t_function where libid = %i and funcname = '%s' and linecount = %i" % (self.libid,self.funcname,self.linecount)
        self.id = self.db.select_id(select_string)
        
        
    def set_linecount(self,linecount):
        self.db.set_linecount(linecount, self.id)
    
    def signature_found(self, libid, funcid, sigpattern, line_offset):
        self.db.insert_hit(libid, funcid, sigpattern, line_offset)

