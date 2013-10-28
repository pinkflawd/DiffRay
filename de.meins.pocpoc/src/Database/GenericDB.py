'''
Created on 26.10.2013

@author: marschalek.m
'''


from sqlalchemy import create_engine, func, MetaData, Table, Column
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.sql import select
from sqlalchemy.types import TypeDecorator, DateTime as DateTimeType


class GenericDB(object):
    '''
    classdocs
    '''


    def __init__(self):

        db = 'sqlite:///a.db'

        # initialize database engine
        engine = create_engine(db, echo=True)
        conn = engine.connect()
        
        metadata = MetaData()
        metadata.create_all(engine)

# table generation (should always be declared - sqlalchemy will make sure
# they're created if they don't exist yet, etc)


