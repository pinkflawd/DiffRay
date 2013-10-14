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
    

mycur = select("""SELECT h.sigpattern, f.funcname, count(*) 
                FROM t_hit h, t_function f where h.funcid=f.id
                and h.libid=2
                group by f.funcname, h.sigpattern
                order by f.funcname, h.sigpattern"""
              )

res = mycur.fetchmany(1000)

while res:
    for pattern7, funcname, hitcount in res:
        fsplit = re.split('\(', funcname, 1, 0)
        print "Win7: %s %s %s" % (fsplit[0],pattern7, hitcount)
        
        select_diff = """select h.sigpattern, count(*) from t_hit h, t_function f where h.funcid=f.id
                         and h.libid=3
                         and h.sigpattern='%s'
                         and f.funcname like '%s%%'
                         group by f.funcname, h.sigpattern""" % (pattern7,fsplit[0])
        cur2 = select(select_diff)
        diff = cur2.fetchall()
        for pattern8, count in diff:
            print "Win8: %s %s %s" % (fsplit[0],pattern8,count)
        print "\n"
    
             
    res = mycur.fetchmany(1000)



