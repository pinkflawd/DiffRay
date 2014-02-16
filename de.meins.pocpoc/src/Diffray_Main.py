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
import traceback
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE


class DiffRay_Main(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(DiffRay_Main, self).__init__(parent)
        self.main_ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'ui', 'diffray_main.ui'), self)
        
        # DATABASE INIT
        self.db = None
        self.backend = ""
        
        # IDB2C
        
        self.button_generateit = self.main_ui.button_generateit
        #self.button_idb2c = self.main_ui.button_idb2c
        self.lineedit_idb2c = self.main_ui.lineedit_idb2c
        self.lineedit_idb2c.setText(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'IDB2C.exe'))
        self.lineedit_idb2c.setReadOnly(1)
                
        self.connect(self.button_generateit, QtCore.SIGNAL('clicked()'), self.generateit)    
        #self.connect(self.button_idb2c, QtCore.SIGNAL('clicked()'), self.setIdb2cPath)    
        
        # PARSING
        self.lineedit_python = self.main_ui.lineedit_python
        self.lineedit_python.setText('C:\\Python27\\python.exe')
        self.button_python = self.main_ui.button_python
        
        self.lineedit_parsing = self.main_ui.lineedit_parsing
        self.button_chp_parsing = self.main_ui.button_chp_parsing
        self.button_chf_parsing = self.main_ui.button_chf_parsing
        self.radio_win7 = self.main_ui.radio_win7
        self.radio_win8 = self.main_ui.radio_win8
        self.radio_c =self.main_ui.radio_c
        self.radio_lst = self.main_ui.radio_lst
        self.button_parseit = self.main_ui.button_parseit
        self.checkbox_flush = self.main_ui.checkbox_flush
        
        self.connect(self.button_python, QtCore.SIGNAL('clicked()'), self.showPythonDialog)
        self.connect(self.button_chf_parsing, QtCore.SIGNAL('clicked()'), self.showFileDialog)
        self.connect(self.button_chp_parsing, QtCore.SIGNAL('clicked()'), self.showDirDialog)
        self.connect(self.button_parseit, QtCore.SIGNAL('clicked()'), self.parseit)

        # CONFIG
        self.combobox_database = self.main_ui.combobox_database
        self.button_config_dialog = self.main_ui.button_config_dialog
        self.button_createdb = self.main_ui.button_createdb
        self.button_flushdb = self.main_ui.button_flushdb
        self.button_updatesigs = self.main_ui.button_updatesigs
        
        self.combobox_database.addItem("SQLITE")
        self.combobox_database.addItem("MSSQL")
        self.button_connect = self.main_ui.button_connect
        self.connect(self.button_connect, QtCore.SIGNAL("clicked()"), self.connectdb)
        
        self.connect(self.button_createdb, QtCore.SIGNAL('clicked()'), self.createdb)
        self.connect(self.button_flushdb, QtCore.SIGNAL('clicked()'), self.createdb)
        self.connect(self.button_updatesigs, QtCore.SIGNAL('clicked()'), self.updatesigs)
        
        self.connect(self.button_config_dialog, QtCore.SIGNAL('clicked()'), self.showConfigDialog)
        
        # LOGGING
        self.textbrowser_logging = self.main_ui.textbrowser_logging
        self.textbrowser_logging.append("DiffRay GUI v0.9 started - initial SQLite DB created in the data directory (dbdbdb.sqlite)")
        self.textbrowser_logging.append("The commanline version is available by starting the Main.py")
        self.textbrowser_logging.append("For more information and a (short) manual check out the project home on https://github.com/pinkflawd/DiffRay")
        
               
    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\')
        self.lineedit_parsing.setText(filename)
        
    def showDirDialog(self):
        dirname = QtGui.QFileDialog.getExistingDirectory(self, 'Open directory', 'C:\\')
        self.lineedit_parsing.setText(dirname)
        
    def setIdb2cPath(self):
        idb2c = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\')
        self.lineedit_idb2c.setText(idb2c)
        
    def showPythonDialog(self):
        pythonp = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\')
        self.lineedit_python.setText(pythonp)

    def showConfigDialog(self):
        dialog = Gui.Settings.Settings()
        dialog.setAcceptDrops(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()
        
    def connectdb(self):
        
        self.textbrowser_logging.append("DB Backend set to %s" % self.combobox_database.currentText())
    
        self.backend = self.combobox_database.currentText()
        if (self.backend == "MSSQL"):
            self.db = Database.MSSqlDB.MSSqlDB()
        elif (self.backend == "SQLITE"):
            self.db = Database.SQLiteDB.SQLiteDB()

    def createdb(self):
        if (self.db is not None):
            self.db.flush_all()
            self.db.create_scheme()
            self.textbrowser_logging.append("Database flushed and recreated (yeah those 2 buttons do the same)")
            self.updatesigs()
            #self.textbrowser_logging.append("Signatures & mappings from signatures.conf/sig_mappings.conf inserted / updated")
        else:
            self.textbrowser_logging.append("Connect to a DB!")
    
    def updatesigs(self):        

        if (self.db is not None):
            signatures = []
    
            try:
                sigfile = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'signatures.conf'))
                
            except:
                self.textbrowser_logging.append("Something went wrong when reading signature file.")
            else:  
                for line in sigfile:
                    #sanitizing the signatures
                    sig = re.sub('\'','', line.rstrip(),0)
                    signatures.append(sig)
                self.db.insert_signatures(signatures)
                sigfile.close()
            
            try:
                sigmapping = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'sig_mapping.conf'))
            except:
                self.textbrowser_logging.append("Something went wrong when accessing the sig_mapping.conf.")
            else:
                for line in sigmapping:
                    map = re.sub('\'','', line.rstrip(),0)
                    arr = re.split('=', map, 1)
                    self.db.update_mappings(arr[0], arr[1])
                sigmapping.close()
                
            self.textbrowser_logging.append("Signatures & mappings from signatures.conf/sig_mappings.conf inserted / updated")
        else:
            self.textbrowser_logging.append("Connect to a DB!")
            
    def generateit(self):
        try:                        
            os.system(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'IDB2C.exe'))
        except:
            self.textbrowser_logging.append("IDB2C.exe is not where it should be! - put it into the util dir")

    def parseit(self):
        
        if (self.db is not None and self.lineedit_python.text().length() > 0):
            try:

                path = str(self.lineedit_parsing.text()).replace('\\','\\\\')
                path = path.replace('/', '\\\\')
    
                if (self.radio_win7.isChecked()):
                    opsys = 'WIN7'
                else:
                    opsys = 'WIN8'
                
                if (self.radio_c.isChecked()):
                    ftype = 'C'
                else:
                    ftype = 'LST'
                    
                try:
                    cmd = str(self.lineedit_python.text()).replace('\\','\\\\')
                    diffray = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Main.py')
                    
                    if os.path.isdir(path):
                        os.system("start %s %s %s %s %s %s %s %s" % (cmd, diffray, '-d', path, '-t', ftype, '-o', opsys))
                    elif os.path.exists(path):
                        os.system("start %s %s %s %s %s %s %s %s" % (cmd, diffray, '-p', path, '-t', ftype, '-o', opsys))
                    else:
                        self.textbrowser_logging.append("Nothing to parse here. Maybe invalid path?")
                except:
                    self.textbrowser_logging.append("Something went wrong when parsing! Check if your input params are ok!")
                 
                else:
                    self.textbrowser_logging.append("Finished Parsing %s" % path)
                        
            except:
                type, value, tb = sys.exc_info()
                self.textbrowser_logging.append("Something went wrong when parsing a library: %s" % (value.message))
                traceback.print_exception(type, value, tb, limit=10, file=sys.stdout)
                self.textbrowser_logging.append("If MSSQL, are the access credentials right? Did you set the right permissions on the DB? Did you actually create a DB on mssql or sqlite?")
        else:
            self.textbrowser_logging.append("Connect to a DB! OR python path wrong.")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = DiffRay_Main()
    window.show()
    app.exec_()