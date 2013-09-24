'''
Created on 12.09.2013

@author: marschalek.m
'''

import Database.MSSqlDB
from Exceptions import ParameterError


class Function(object):
    '''
    classdocs
    '''


    def __init__(self, libid, funcname, linecount):
        
        #if u wish so, check libid if integer. but basically, not necessary     
        self.libid = libid
        
        if len(funcname) < 499:
            self.funcname = funcname
        else:
            raise ParameterError, "Funcname for function object is too long, max 499 chars."
        
        if linecount < 2147483647: 
            self.linecount = linecount
        else:
            raise ParameterError, "Linecount exceeds int range - weiiird should never happen."
        
        # might throw exception - theres no throws keyword :/
        self.db = Database.MSSqlDB.MSSqlDB()
        self.db.insert_function(self.libid,self.funcname,self.linecount)
        select_string = "select id from [Poc].[dbo].[t_function] where libid = %i and funcname = '%s' and linecount = %i" % (self.libid,self.funcname,self.linecount)
        self.id = self.db.select_id(select_string)
        
        
    def set_linecount(self,linecount):
        self.db.set_linecount(linecount, self.id)
    
    def signature_found(self, libid, funcid, sigpattern, line_offset):
        self.db.insert_hit(libid, funcid, sigpattern, line_offset)