'''
Created on 13.10.2013

@author: Marion
'''


import sqlite3
import os.path
from Exceptions import DatabaseError
import re
import Parsing.Function

try:
    localdb = sqlite3.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'pocpoc2.sqlite'))
    localdb.row_factory = sqlite3.Row
except:
    raise DatabaseError, "Connection to DB cant be established."

function = Parsing.Function.Function(1, 'DllMain(HMODULE hLibModule, int a2, int a3)', 0, 'sqlite')
