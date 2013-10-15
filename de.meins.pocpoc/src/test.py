'''
Created on 13.10.2013

@author: Marion
'''


import sqlite3
import os.path
from Exceptions import DatabaseError
import re

try:
    localdb = sqlite3.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'pocpoc2.sqlite'))
    localdb.row_factory = sqlite3.Row
except:
    raise DatabaseError, "Connection to DB cant be established."


def select(select_string):
    try:
        cursor = localdb.cursor()
        cursor.execute(select_string)
    except:
        raise DatabaseError, "An Error occurred when executing a select."
    else:
        return cursor
    


cur_win7 = localdb.select_diff_win7(2)

res = cur_win7.fetchmany(1000)

print "Function_Name;Pattern;Win7_Hits;Win8_Hits"

while res:
    for pattern7, funcname, hitcount7 in res:
        fsplit = re.split('\(', funcname, 1, 0)
        
        cur_win8 = localdb.select_diff_win8(pattern7,fsplit[0])
        diff = cur_win8.fetchone()
        
        if diff:
            print "%s;%s;%s;%s" % (fsplit[0],pattern7,hitcount7,diff['co'])
        else:
            print "%s;%s;%s;" % (fsplit[0],pattern7,hitcount7)

    
             
    res = cur_win7.fetchmany(1000)



