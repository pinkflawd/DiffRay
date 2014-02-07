'''
Created on 01.02.2014

@author: marschalek.m
'''

import sys, os
from PyQt4 import QtGui, QtCore, uic
import Gui.Settings

from optparse import OptionParser
import Parsing.Library
import Diffing.Info
import Database.MSSqlDB
import Database.SQLiteDB
import logging.config
import re



class DiffRay_Main(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(DiffRay_Main, self).__init__(parent)
        self.main_ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'ui', 'diffray_main.ui'), self)
        
        # DATABASE CONNECTION
        self.db = Database.SQLiteDB.SQLiteDB()
        self.backend = "SQLITE"
        
        # PARSING
        self.lineedit_parsing = self.main_ui.lineedit_parsing
        self.button_chp_parsing = self.main_ui.button_chp_parsing
        self.button_chf_parsing = self.main_ui.button_chf_parsing

        # CONFIG
        self.combobox_database = self.main_ui.combobox_database
        self.button_config_dialog = self.main_ui.button_config_dialog
        
        # LOGGING
        self.textbrowser_logging = self.main_ui.textbrowser_logging
        self.textbrowser_logging.append("logging gonna go here")
        
        self.connect(self.button_chf_parsing, QtCore.SIGNAL('clicked()'), self.showFileDialog)
        self.connect(self.button_chp_parsing, QtCore.SIGNAL('clicked()'), self.showDirDialog)
        
        self.combobox_database.addItem("SQLITE")
        self.combobox_database.addItem("MSSQL")
                
        self.connect(self.combobox_database, QtCore.SIGNAL("currentIndexChanged(int)"), self.connectDB)
        self.connect(self.button_config_dialog, QtCore.SIGNAL('clicked()'), self.showConfigDialog)
        

    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\')
        self.lineedit_parsing.setText(filename)
        
    def showDirDialog(self):
        dirname = QtGui.QFileDialog.getExistingDirectory(self, 'Open directory', 'C:\\')
        self.lineedit_parsing.setText(dirname)
        
    def showConfigDialog(self):
        dialog = Gui.Settings.Settings()
        dialog.setAcceptDrops(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()
        
    def connectDB(self):
        
        log = "LOG - DB Backend set to %s" % self.sender().currentText()
        self.textbrowser_logging.append("LOG - DB Backend set to %s" % self.sender().currentText())
    
        self.backend = self.sender().currentText()
        if (self.backend == "MSSQL"):
            self.db = Database.MSSqlDB.MSSqlDB()
        elif (self.backend == "SQLITE"):
            self.db = Database.SQLiteDB.SQLiteDB()

        
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = DiffRay_Main()
    window.show()
    app.exec_()