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
            # set row factory to Row type for accessing rows as dictionaries
            self.localdb.row_factory = sqlite3.Row
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
            raise DatabaseError, "An Error occurred when executing a delete."
        else:
            self.localdb.commit()
            
    def update(self, update_string):
        try:
            cursor = self.localdb.cursor()
            cursor.execute(update_string)
        except:
            raise DatabaseError, "An Error occurred when executing an update."
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
        
    def select_funcid(self, libid, funcname, linecount):
        select_string = "select id from t_function where libid = %i and funcname = '%s' and linecount = %i" % (libid,funcname,linecount)
        id = self.select_id(select_string)
        return id
    
    def select_libid(self, filemd5):
        select_string = "select id from t_library where libmd5 = '%s'" % filemd5
        id = self.select_id(select_string)
        return id

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
        delete_string = "delete from t_function where libid = %i" % libid
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
            return False
        else:
            self.log.info("Library with id %s already exists" % filemd5)
            return True
                
                
    def insert_function(self, libid, funcname, linecount):
        insert_string = "insert into t_function (libid, funcname, linecount) values (%i, '%s', %i)" % (libid, funcname, linecount)
        self.insert(insert_string)
        
    def insert_signatures(self, signatures):
        self.flush_signature()
        for sig in signatures:
            insert_string = "insert into t_signature (sigpattern) values ('%s')" % sig
            self.insert(insert_string)
        self.log.info("Signatures inserted/updated")
        
    def update_mappings(self, sig, map):
        insert_string = "update t_signature set mapping='%s' where sigpattern = '%s'" % (map, sig)
        self.update(insert_string)
        
    def insert_hit(self, libid, funcid, sigpattern, line_offset):
        insert_string = "insert into t_hit (libid, funcid, sigpattern, line_offset) values (%i, %i, '%s', %i)" % (libid, funcid, sigpattern, line_offset)
        self.insert(insert_string)
    
    
    def set_linecount(self, linecount, funcid):
        update_string = "update t_function set linecount = %i where id = %i" % (linecount, funcid)
        self.update(update_string)
        
        
    ### INFO TASKS
    
    # gets libids for performing more Info tasks
    def select_libs_byname(self, libname):
        select_string = "select id, libname, os, filetype from t_library where libname like '%%%s%%'" % libname
        res = self.select(select_string)
        return res
    
    # returns a set of hitcounts, grouped by funcname and sigpattern for whole lib
    def select_diff_one(self, libid):
        select_string = """SELECT h.sigpattern, f.funcname, count(*) co
                FROM t_hit h, t_function f where h.funcid=f.id
                and h.libid=%s
                group by f.funcname, h.sigpattern
                order by f.funcname, h.sigpattern""" % libid
                
        cur_win7 = self.select(select_string)
        return cur_win7

    
    # returns a set of hitcounts, matching funcname and sigpattern of a line of a win7_diff set
    def select_diff_two(self, libid, pattern, funcname):
        select_string = """select count(*) co from t_hit h, t_function f where h.funcid=f.id
                         and h.libid=%s
                         and h.sigpattern='%s'
                         and f.funcname like '%%%s%%'
                         group by f.funcname, h.sigpattern""" % (libid,pattern,funcname)
        cur_win8 = self.select(select_string)
        return cur_win8
    
    #returns all hits found for a certain libid
    def select_lib_all(self, libid):
        select_string = """select l.libname, f.funcname, h.sigpattern, h.line_offset from t_hit h, t_function f, t_library l 
                           where h.libid = l.id and h.funcid = f.id and h.libid=%s""" % libid
        return self.select(select_string)
 
    #checks if function exists in library
    def select_function(self, funcname, libid):
        select_string = """select id from t_function where funcname like '%s%%' and libid=%s""" % (funcname, libid)
        cur = self.select(select_string)
        row = cur.fetchone()
        if row:
            return True
        else:
            return False     
        
    # get the os of a lib           
    def select_os(self,libid):
        select_string = "select os from t_library where id = %i" % libid
        return self.select(select_string)
        
    # get mappings in signature table
    def select_mappings(self):
        select_string = "select * from t_signature where mapping not null"
        return self.select(select_string)
    
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
                        sigpattern text primary key,
                        mapping text
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
        

