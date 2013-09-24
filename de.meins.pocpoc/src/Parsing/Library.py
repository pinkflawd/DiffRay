'''
Created on 05.09.2013

@author: marschalek.m
'''

import Database.MSSqlDB
import Function
import hashlib
import re
import logging.config
import os

from Exceptions import ParameterError, FileError

class Library(object):
    
    try:
        logging.config.fileConfig(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'))
        log = logging.getLogger('Library')
    except:
        # here could go some configuration of a default logger -- me too lazy
        print "Error, logger.conf not found or broken. Check on http://docs.python.org/2/howto/logging.html what to do."
        exit(1)


    def __init__(self, path, os):
        
        if len(path) < 300:
            self.path = path
        else:
            raise ParameterError, "Path Parameter too long! max. 299" 
            
        if len(os) < 5:
            self.os = os
        else:
            raise ParameterError, "OS Parameter too long! Expects Win7 or Win8, max. 4"
 

        try:
            self.file = open(self.path)
        except IOError:
            raise FileError, "Cant open given file for parsing! IOError."
        except:
            raise FileError, "Cant open given file for parsing! Unknown Error."
            
        else:    
            self.log.info("parsing %s for %s" % (self.path, self.os))
            
            data = self.file.read()
            self.filemd5 = hashlib.md5(data).hexdigest()
            
            self.db = Database.MSSqlDB.MSSqlDB()
            self.db.insert_library(self.filemd5,self.path,self.os)
            
            select_string = "select id from t_library where libmd5 = 0x%s" % self.filemd5
            self.id = self.db.select_id(select_string)
        
        
    def parse_cfile(self):
        
        # Regexes to scan for function offsets
        f_off = re.compile('^[^\/|\s|#].+(stdcall|cdecl|thiscall|fastcall|userpurge|usercall).+[^\)].*$')   
        semico = re.compile('[;|=]')
        comment = re.compile('^[\/\/|#]')

        linecount = 0
        #func_offset = None
        function = None
        
        #TODO try
        try:
            self.file = open(self.path) # file handle doesnt survive the method switch?!
        except:
            raise FileError, "Can't open file to parse. At parse_cfile."
        
        else:
            
            signatures = self.db.select_signatures()
            self.log.info("Parsing...... pls wait")
            
            for line in self.file:
                if f_off.search(line) and not semico.search(line):
                    
                    if function is not None:
                        # update linecount to database
                        function.set_linecount(linecount)
                   
                    # create new function (object) with linecount 0
                    function = Function.Function(self.id, line.rstrip(), 0)
                    linecount = 0
                    
                elif function is not None and not comment.search(line):                      #inside a function and not a comment line
      
                    for sig in signatures:
                        sigscan = re.compile(sig)
                        if sigscan.search(line):
                            function.signature_found(function.libid,function.id,sig,linecount+1)
                                            
                    # every line: count++
                    linecount = linecount+1
                    
                else:
                    pass
            
                    # dont forget last function ;)
            function.set_linecount(linecount)
 
        
    def flush_me(self):
        self.db.flush_library(self.id)
        self.log.info("Library %s with id %s flushed" % (self.path, self.filemd5))
        

        
        