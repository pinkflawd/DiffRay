'''
Created on 05.09.2013

@author: pinkflawd
'''

import Function
import hashlib
import re
import logging.config
import os
from Exceptions import ParameterError, FileError


class Library(object):
    
    '''
    LIBRARY CLASS
    represents a library in the database
    '''
    
    try:
        logging.config.fileConfig(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'))
        log = logging.getLogger('Library')
    except:
        # here could go some configuration of a default logger -- me too lazy
        print "Error, logger.conf not found or broken. Check on http://docs.python.org/2/howto/logging.html what to do."
        exit(1)


    def __init__(self, path, os, ftype, database):
        
        if len(path) < 300:
            sanipath = re.sub('\'','', path,0)
            self.path = sanipath
        else:
            raise ParameterError, "Path Parameter too long! max. 299" 
            
        if len(os) < 5:
            self.os = os
        else:
            raise ParameterError, "OS Parameter too long! Expects Win7 or Win8, max. 4"
        
        if len(ftype) < 4:
            self.ftype = ftype
        else:
            raise ParameterError, "Type can be c or C or lst or LST, literally nothing else."

        try:
            self.file = open(self.path)
        except:
            raise FileError, "Cant open given file for parsing! Unknown Error."
            
        else:    
            self.log.info("parsing %s for %s" % (self.path, self.os))
            
            data = self.file.read()
            self.filemd5 = hashlib.md5(data).hexdigest()
            self.file.close()
            
            if (database == "mssql"):
                import Database.MSSqlDB
                self.db = Database.MSSqlDB.MSSqlDB()
                self.backend = "mssql"
            else:
                import Database.SQLiteDB
                self.db = Database.SQLiteDB.SQLiteDB()
                self.backend = "sqlite"
                
            self.existant = self.db.insert_library(self.filemd5,self.path,self.os,self.ftype)
            self.id = self.db.select_libid(self.filemd5)
           
        
    def parse_cfile(self):
        
        # Regexes to scan for whatever needed
        f_off = re.compile('^[^\/|\s|#].+(stdcall|cdecl|thiscall|fastcall|userpurge|usercall).+[^\)].*$')   
        semico = re.compile('[;|=]')
        comment = re.compile('^[\/\/|#]')
        brackon = re.compile('{')
        brackoff = re.compile('}')

        linecount = 0
        brackflag = 0
        function = None
        
        try:
            self.file = open(self.path)
        except:
            raise FileError, "Can't open file to parse. At parse_cfile."
        
        else:
            
            self.log.info("Parsing...... pls wait")
            
            for line in self.file:
                
                if f_off.search(line) and not semico.search(line): ###### FIND FUNCTIONS WITHOUT CALLING CONV.

                    # create new function (object) with linecount 0
                    if function is not None:
                        self.log.error("Something wrong with the brackets? %s" % function.funcname)
                        print brackflag
                    function = Function.Function(self.id, line.rstrip(), 0, self.backend)
                    linecount = 0
                    brackflag = 0
                    
                elif function is not None and not comment.search(line):                      #inside a function and not a comment line
      
                    ### here: check if line worth scanning: enough characters to fit a signature :P
                    rline = line.replace(' ','')
                    # cut off comments
                    blubb = rline.partition('//')
                    rline = blubb[0]
                    
                    if (len(rline) > 11):
                        signatures = self.db.select_signatures()
                        for sig in signatures:
                            sigscan = re.compile(sig['sigpattern'])
                            if sigscan.search(line):
                                print sig['sigpattern']
                                ### here: check for mapping, if exists, replace sig
                                if (sig['mapping'] is not None):
                                    function.signature_found(function.libid,function.id,sig['mapping'],linecount+1)
                                    #print "MAPPING found %s in %s" % (sig['mapping'], line.rstrip())
                                else:
                                    function.signature_found(function.libid,function.id,sig['sigpattern'],linecount+1)
                        signatures.close()
                    
                    if (brackon.search(rline)):
                        brackflag += 1

                    if (brackoff.search(rline)):
                        brackflag -= 1
                        if (brackflag == 0):
                            function.set_linecount(linecount+1)
                            #print "ending func %s" % function.funcname
                            function = None
                                                        
                    if function is not None:                  
                        # every line: count++
                        linecount = linecount+1
                    
                else:
                    pass
            
            if function is not None:
                self.log.error("Something wrong with the brackets? %s" % function.funcname)
            else:
                self.log.info("Success.")
            
            self.file.close()
 
 
    ### DEPRECATED ###
 
    def parse_lstfile(self):
        
        # redundant code, i know, sorry..
        
        # Regexes to scan for function offsets
        f_off = re.compile('^\.[a-zA-Z]+:[0-9a-fA-F]+.+(stdcall|cdecl|thiscall|fastcall|userpurge|usercall)')   
        f_off3 = re.compile('START OF FUNCTION CHUNK')

        linecount = 0
        function = None
        
        try:
            self.file = open(self.path)
        except:
            raise FileError, "Can't open file to parse. At parse_lstfile."
        
        else:
            
            signatures = self.db.select_signatures()
            self.log.info("Parsing...... pls wait")
            
            for line in self.file:
                if (f_off.search(line) or f_off3.search(line)):
                
                    if function is not None:
                        # update linecount to database
                        function.set_linecount(linecount)
                   
                    # create new function (object) with linecount 0
                    function = Function.Function(self.id, line.rstrip(), 0, self.backend)
                    linecount = 0
                    
                elif function is not None:                      #inside a function and not a comment line
      
                    for sig in signatures:
                        regex = "^\.[a-zA-Z]+:[0-9a-fA-F]+\s+call.*"
                        regex += sig
                        sigscan = re.compile(regex)
                        if sigscan.search(line):
                            function.signature_found(function.libid,function.id,sig,linecount+1)
                                            
                    # every line: count++
                    linecount = linecount+1
                    
                else:
                    pass
            
                    # dont forget last function ;)
            function.set_linecount(linecount)
            self.file.close()
        
        
    def flush_me(self):
        self.db.flush_library(self.id)
        self.log.info("Library %s with id %s flushed" % (self.path, self.filemd5))
        
