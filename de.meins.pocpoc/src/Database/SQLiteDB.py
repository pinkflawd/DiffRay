'''
Created on 18.09.2013

@author: pinkflawd
'''

import sqlite3
import logging.config
import os.path
from Exceptions import DatabaseError



class SQLiteDB(object):
    
    '''
    SQLiteDB CLASS
    interaction with sqlite, waaaay slower than mssql but totally portable ^^
    '''

    try:
        logging.config.fileConfig(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'))
        log = logging.getLogger('SQLiteDB')
    except:
        # here could go some configuration of a default logger -- me too lazy
        print "Error, logger.conf not found or broken. Check on http://docs.python.org/2/howto/logging.html what to do."
        exit(1)

    
    def __init__(self):
        try:
            self.localdb = sqlite3.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'data', 'pocpoc2.sqlite'))
        except:
            raise DatabaseError, "Connection to DB cant be established."
        
    def __del__(self):
        try:
            self.localdb.close()
        except:
            pass
    
    ###########################
    # Base Operations         #
    ###########################

    def select(self, select_string):
        try:
            cursor = self.localdb.cursor()
            cursor.execute(select_string)
        except:
            raise DatabaseError, "An Error occurred when executing a select."
        else:
            return cursor
        
    def insert(self, insert_string):
        
        try:
            cursor = self.localdb.cursor()
            cursor.execute(insert_string)
        except:
            raise DatabaseError, "An Error occurred when executing an insert."
        else:
            self.localdb.commit()
            
    def delete(self, delete_string):
        try:
            cursor = self.localdb.cursor()
            cursor.execute(delete_string)
        except:
            print delete_string
            raise DatabaseError, "An Error occurred when executing a delete."
        else:
            self.localdb.commit()
            
    def update(self, update_string):
        try:
            cursor = self.localdb.cursor()
            cursor.execute(update_string)
        except:
            raise DatabaseError, "An Error occurred when executing a delete."
        else:
            self.localdb.commit()
        

    ###########################
    # Extended Operations     #
    ###########################
            
    def select_id(self, select_string):
        cur = self.select(select_string)
        row = cur.fetchone()
        if row:
            return row[0]
        else:
            return 0

    def select_signatures(self):
        select_string = "select sigpattern from t_signature"
        res = self.select(select_string)
        signatures = []
        for sig in res:
            signatures.append(sig[0])
        return signatures
            
    def flush_all(self):

        drop_string = """drop table if exists t_hit"""
        self.delete(drop_string)
                
        drop_string = """drop table if exists t_function"""
        self.delete(drop_string)
        
        drop_string = """drop table if exists t_library"""
        self.delete(drop_string)
        
        drop_string = """drop table if exists t_signature"""
        self.delete(drop_string)

        self.log.info("Database flushed")
 
    def flush_library(self, libid):
        delete_string = "delete from t_hit where libid = %i" % libid
        self.delete(delete_string)
        delete_string = "delete from t_hit where libid = %i" % libid
        self.delete(delete_string)
        
    def flush_signature(self):
        delete_string = "delete from t_signature"
        self.delete(delete_string)
        
    def insert_library(self, filemd5, filename, os, ftype):
        select_string = "select id from t_library where libmd5 = '%s'" % filemd5
        libid = self.select_id(select_string)
        if libid == 0:
            insert_string = "insert into t_library (libmd5, libname, os, filetype) values ('%s','%s', '%s', '%s')" % (filemd5, filename, os, ftype)
            self.insert(insert_string)
            self.log.info("Library %s with id %s created" %(filename, filemd5))
        else:
            self.log.info("Library with id %s already exists" % filemd5)
                
                
    def insert_function(self, libid, funcname, linecount):
        insert_string = "insert into t_function (libid, funcname, linecount) values (%i, '%s', %i)" % (libid, funcname, linecount)
        self.insert(insert_string)
        
    def insert_signatures(self, signatures):
        self.flush_signature()
        for sig in signatures:
            insert_string = "insert into t_signature (sigpattern) values ('%s')" % sig
            self.insert(insert_string)
        self.log.info("Signatures inserted/updated")
        
    def insert_hit(self, libid, funcid, sigpattern, line_offset):
        insert_string = "insert into t_hit (libid, funcid, sigpattern, line_offset) values (%i, %i, '%s', %i)" % (libid, funcid, sigpattern, line_offset)
        self.insert(insert_string)
    
    
    def set_linecount(self, linecount, funcid):
        update_string = "update t_function set linecount = %i where id = %i" % (linecount, funcid)
        self.update(update_string)
        
        
    ###########################
    # Scheme Re-Creation      #
    # t_library               #
    # t_function              #
    # t_signature             #
    # t_hit                   # 
    ###########################
        
    def create_scheme(self):
        
        create_string = """CREATE TABLE t_library (
                           id integer primary key,
                           libmd5 blob,
                           libname text,
                           os text,
                           filetype text
                           )"""
        self.insert(create_string)

        create_string = """create table t_function (
                        id integer primary key,
                        libid integer not null,
                        funcname text,
                        linecount integer,
                        foreign key(libid) references t_library(id)
                        )"""
        self.insert(create_string)
               
        create_string = """create table t_signature (
                        sigpattern text primary key
                        )"""
        self.insert(create_string)
        
       
        create_string = """create table t_hit (
                        id integer primary key,
                        libid integer not null,
                        funcid integer not null,
                        sigpattern text not null,
                        line_offset integer,
                        foreign key(libid) references t_library(id),
                        foreign key(funcid) references t_function(id),
                        foreign key(sigpattern) references t_signature(sigpattern)
                        )"""
        
        self.insert(create_string)

        self.log.info("Database recreated")
        
