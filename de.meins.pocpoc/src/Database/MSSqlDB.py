'''
Created on 06.09.2013

@author: marschalek.m
'''

import ConfigParser
import pymssql
import os.path

class MSSqlDB(object):
    '''
    classdocs
    '''


    def __init__(self):
        
        # TODO sanitize & throw around exceptions
        
        conf = ConfigParser.ConfigParser()
        conf.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'conf', 'static.conf'))
        
        dbhost = conf.get('Database', 'dbhost')
        dbuser = conf.get('Database', 'dbuser')
        dbpassword = conf.get('Database', 'dbpassword')
        dbname = conf.get('Database', 'dbname')
        
        self.localdb = pymssql.connect(host=dbhost, user=dbuser, password=dbpassword, database=dbname, as_dict=True)  # @UndefinedVariable

    
    def __del__(self):
        self.localdb.close()
        
        
    ###########################
    # Base Operations         #
    ###########################
    
    # TODO on inserts check if table exists & stuff. try catch? 
    # TODO parametrizised queries!!!
    
    
    def select(self, select_string):
        cursor = self.localdb.cursor()
        cursor.execute(select_string)
        return cursor
    
    def insert(self, insert_string):
        cursor = self.localdb.cursor()
        cursor.execute(insert_string)
        self.localdb.commit()
        
        
    def insert_many(self, insert_string, inserts):
        cursor = self.localdb.cursor()
        for thing in inserts:
            cursor.execute(insert_string, thing)
        self.localdb.commit()
                
        
    def delete(self, delete_string):
        cursor = self.localdb.cursor()
        cursor.execute(delete_string)
        self.localdb.commit()
        
    def update(self, update_string):
        cursor = self.localdb.cursor()
        cursor.execute(update_string)
        self.localdb.commit()


    ###########################
    # Extended Operations     #
    ###########################
    
    # TODO rename id columns, aggregate select_id function
    
    def select_id(self, select_string):
        cur = self.select(select_string)
        row = cur.fetchone()
        if row:
            return row['id']
        else:
            return 0

    def select_signatures(self):
        select_string = "select sigpattern from [Poc].[dbo].[t_signature]"
        res = self.select(select_string)
        signatures = []
        for sig in res:
            signatures.append(sig['sigpattern'])
        return signatures
    
    def flush_all(self):
        drop_string = """IF OBJECT_ID('[Poc].[dbo].[t_hit]','U') IS NOT NULL
                      drop table t_hit"""
        self.delete(drop_string)


        drop_string = """IF OBJECT_ID('[Poc].[dbo].[t_function]','U') IS NOT NULL
                      drop table t_function"""
        self.delete(drop_string)
        
        drop_string = """IF OBJECT_ID('[Poc].[dbo].[t_library]','U') IS NOT NULL
                      drop table t_library"""
        self.delete(drop_string)
        
        drop_string = """IF OBJECT_ID('[Poc].[dbo].[t_signature]','U') IS NOT NULL
                      drop table t_signature"""
        self.delete(drop_string)
        
        print "LOG MSSqlDB - Database flushed"
    
    def flush_library(self, libid):
        delete_string = "delete from [Poc].[dbo].[t_hit] where libid = %s" % libid
        self.delete(delete_string)
        delete_string = "delete from [Poc].[dbo].[t_function] where libid = %s" % libid
        self.delete(delete_string)
        
        
    def flush_signature(self):
        delete_string = "delete from [Poc].[dbo].[t_signature]"
        self.delete(delete_string)
        
    
    def insert_library(self, filemd5, filename, os):
        
        select_string = "select id from [Poc].[dbo].[t_library] where libmd5 = 0x%s" % filemd5
        libid = self.select_id(select_string)
        if libid == 0:
            insert_string = "insert into [Poc].[dbo].[t_library] (libmd5, libname, os) values (0x%s,'%s', '%s')" % (filemd5, filename, os)
            self.insert(insert_string)
            print "LOG MSSqlDB - created library %s with md5 %s" %(filename, filemd5)
        else:
            print "LOG MSSqlDB - library with id %s already exists" % filemd5
                
                
    def insert_function(self, libid, funcname, linecount):
        insert_string = "insert into [Poc].[dbo].[t_function] (libid, funcname, linecount) values (%i, '%s', %i)" % (libid, funcname, linecount)
        self.insert(insert_string)
    
        
    def insert_signatures(self, signatures):
        self.flush_signature()
        for sig in signatures:
            insert_string = "insert into [Poc].[dbo].[t_signature] (sigpattern) values ('%s')" % sig
            self.insert(insert_string)
        print "LOG MSSqlDB - Signatures inserted/updated"
        
        
    def insert_hit(self, libid, funcid, sigpattern, line_offset):
        insert_string = "insert into [Poc].[dbo].[t_hit] (libid, funcid, sigpattern, line_offset) values (%i, %i, '%s', %i)" % (libid, funcid, sigpattern, line_offset)
        self.insert(insert_string)
    
    
    def set_linecount(self, linecount, funcid):
        update_string = "update [Poc].[dbo].[t_function] set linecount = %i where id = %i" % (linecount, funcid)
        self.update(update_string)
        
    ###########################
    # Scheme Re-Creation      #
    # t_library               #
    # t_function              #
    # t_signature             #
    ###########################
        
    def create_scheme(self):
        
        create_string = """create table t_library (
                        id int identity(1,1) primary key not null,
                        libmd5 [binary](16) not null,
                        libname    varchar(300) not null,
                        os        varchar(4)
                        )"""
        self.insert(create_string)

        create_string = """create table t_function (
                        id int identity(1,1) primary key not null,
                        libid int not null,
                        funcname varchar(500),
                        linecount int
                        )"""
        self.insert(create_string)
               
        create_string = """ALTER TABLE [Poc].[dbo].[t_function] WITH CHECK ADD FOREIGN KEY([libid])
                        REFERENCES [Poc].[dbo].[t_library] ([id])"""
        self.insert(create_string)
        
        create_string = """create table t_signature (
                        sigpattern varchar(100) primary key not null,
                        )"""
        self.insert(create_string)
        
        
        create_string = """create table t_hit (
                        id int identity(1,1) primary key not null,
                        libid int not null,
                        funcid int not null,
                        sigpattern varchar(100) not null,
                        line_offset int
                        )"""
        self.insert(create_string)
        
        
        create_string = """ALTER TABLE [Poc].[dbo].[t_hit] WITH CHECK ADD FOREIGN KEY([libid])
                        REFERENCES [Poc].[dbo].[t_library] ([id])"""
        self.insert(create_string)        
        
        create_string = """ALTER TABLE [Poc].[dbo].[t_hit] WITH CHECK ADD FOREIGN KEY([funcid])
                        REFERENCES [Poc].[dbo].[t_function] ([id])"""
        self.insert(create_string) 
        
        create_string = """ALTER TABLE [Poc].[dbo].[t_hit] WITH CHECK ADD FOREIGN KEY([sigpattern])
                        REFERENCES [Poc].[dbo].[t_signature] ([sigpattern])"""
        self.insert(create_string)


        print "LOG MSSqlDB - Database recreated"


