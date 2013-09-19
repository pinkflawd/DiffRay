'''
Created on 12.09.2013

@author: marschalek.m
'''

import Database.MSSqlDB

class Function(object):
    '''
    classdocs
    '''


    def __init__(self, libid, funcname, linecount):
        
        self.libid = libid
        self.funcname = funcname
        self.linecount = linecount
        
        
        self.db = Database.MSSqlDB.MSSqlDB()
        self.db.insert_function(self.libid,self.funcname,self.linecount)
        select_string = "select id from [Poc].[dbo].[t_function] where libid = %i and funcname = '%s' and linecount = %i" % (self.libid,self.funcname,self.linecount)
        self.id = self.db.select_id(select_string)
        
        
    def set_linecount(self,linecount):
        self.db.set_linecount(linecount, self.id)
    
    def signature_found(self, libid, funcid, sigpattern, line_offset):
        self.db.insert_hit(libid, funcid, sigpattern, line_offset)