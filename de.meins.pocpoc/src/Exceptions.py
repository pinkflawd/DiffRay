'''
Created on 18.09.2013

@author: marschalek.m
'''

import exceptions

class UndefinedError(exceptions.Exception):
    '''
    classdocs
    '''


    def __init__(self):
        pass
    


class DatabaseError(Exception):
    
    def __init__(self):
        pass


class ParameterError(Exception):
    
    def __init__(self):
        pass

class FileError(Exception):
    
    def __init__(self):
        pass