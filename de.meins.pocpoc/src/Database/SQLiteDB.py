'''
Created on 18.09.2013

@author: marschalek.m
'''

import sqlite3
import logging.config
import os.path
from Exceptions import DatabaseError



class SQLiteDB(object):

    try:
        logging.config.fileConfig(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'))
        log = logging.getLogger('MSSqlDB')
    except:
        # here could go some configuration of a default logger -- me too lazy
        print "Error, logger.conf not found or broken. Check on http://docs.python.org/2/howto/logging.html what to do."
        exit(1)

    
    def __init__(self):
        pass
    