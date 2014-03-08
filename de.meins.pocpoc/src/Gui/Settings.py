'''
Created on 04.02.2014

@author: marschalek.m
'''


import os
import sys

from PyQt4 import QtGui, QtCore, uic


class Settings(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'ui', 'settings.ui'), self)
        
        self.textEdit = self.ui.textEdit
        self.te_state = TeState.EMPTY
        
        # settings buttons
        self.signatures_button = self.ui.signatures_button
        self.mappings_button = self.ui.mappings_button
        self.database_button = self.ui.database_button
        self.log_button = self.ui.log_button
        
        self.connect(self.signatures_button, QtCore.SIGNAL("clicked()"), self.on_signatures_button_clicked)
        self.connect(self.mappings_button, QtCore.SIGNAL("clicked()"), self.on_mappings_button_clicked)
        self.connect(self.database_button, QtCore.SIGNAL("clicked()"), self.on_database_button_clicked)
        self.connect(self.log_button, QtCore.SIGNAL("clicked()"), self.on_log_button_clicked)
        
        # save and cancel
        self.cancel_button = self.ui.cancel_button
        self.save_button = self.ui.save_button
        self.connect(self.cancel_button, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))
    
        
    def on_signatures_button_clicked(self):
        fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'signatures.conf'))
        self.textEdit.setText(fileh.read())
        self.te_state = TeState.SIGNATURES
        
    def on_mappings_button_clicked(self):
        fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'sig_mapping.conf'))
        self.textEdit.setText(fileh.read())
        self.te_state = TeState.MAPPINGS
        
    def on_database_button_clicked(self):
        fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'mssql.conf'))
        self.textEdit.setText(fileh.read())
        self.te_state = TeState.DATABASE
        
    def on_log_button_clicked(self):
        fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'))
        self.textEdit.setText(fileh.read())
        self.te_state = TeState.LOGGING
            
    
    def on_save_button_clicked(self):
        
        fileh = None
        
        # TODO change conf filenames to constants
        # TODO update database on change
        
        if (self.te_state == TeState.EMPTY):
            pass
        elif (self.te_state == TeState.SIGNATURES):
            fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'signatures.conf'), 'w')
        elif (self.te_state == TeState.MAPPINGS):
            fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'sig_mapping.conf'), 'w')
        elif (self.te_state == TeState.DATABASE):
            fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'mssql.conf'), 'w')
        else: # (self.te_state == TeState.LOGGING)
            fileh = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..', 'conf', 'logger.conf'), 'w')
        
        if (fileh != None):
            fileh.write(self.textEdit.toPlainText())
            fileh.close()
        
        #self.close()

class TeState():
    EMPTY = 1
    SIGNATURES = 2
    MAPPINGS = 3
    DATABASE = 4
    LOGGING = 5

