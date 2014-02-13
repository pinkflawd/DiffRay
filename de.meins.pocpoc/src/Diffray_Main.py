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


class DiffRay_Main(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(DiffRay_Main, self).__init__(parent)
        self.main_ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'ui', 'diffray_main.ui'), self)
        
        # DATABASE INIT
        self.db = None
        self.backend = ""
        
        # IDB2C
        
        self.button_generateit = self.main_ui.button_generateit
        self.connect(self.button_generateit, QtCore.SIGNAL('clicked()'), self.generateit)        
        
        # PARSING
        self.lineedit_parsing = self.main_ui.lineedit_parsing
        self.button_chp_parsing = self.main_ui.button_chp_parsing
        self.button_chf_parsing = self.main_ui.button_chf_parsing
        self.radio_win7 = self.main_ui.radio_win7
        self.radio_win8 = self.main_ui.radio_win8
        self.radio_c =self.main_ui.radio_c
        self.radio_lst = self.main_ui.radio_lst
        self.button_parseit = self.main_ui.button_parseit
        self.checkbox_flush = self.main_ui.checkbox_flush
        
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
        print "here"
        pass

    def parseit(self):
        
        if (self.db is not None):
            try:
                
                lib_files = []
                path = str(self.lineedit_parsing.text())
                
                if os.path.isdir(path):
                    lib_files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
                elif os.path.exists(path):
                    lib_files.append(path)
                    
                if (self.radio_win7.isChecked()):
                    opsys = 'WIN7'
                else:
                    opsys = 'WIN8'
                
                if (self.radio_c.isChecked()):
                    ftype = 'C'
                else:
                    ftype = 'LST'
    
                for lib_file in lib_files:  
                    self.textbrowser_logging.append("Parsing %s for %s" % (lib_file, opsys))
                    lib = Parsing.Library.Library(lib_file, opsys, ftype, self.backend)
                    
                    # if lib exists - flush functions
                    # if lib exists and no-flush active - continue
                    if (lib.existant == True and self.checkbox_flush.isChecked()) or lib.existant == False:
                        lib.flush_me()
                    
                        if ftype == 'C':
                            lib.parse_cfile()
                        elif ftype == 'LST':
                            lib.parse_lstfile()
                        else:
                            self.textbrowser_logging.append("Wrong file type! Either c or C or lst or LST, pleeease dont mix caps with small letters, dont have all day for op parsing ;)")
                    
                        self.textbrowser_logging.append("Finished Parsing")
                    else:
                        self.textbrowser_logging.append("Nothing to parse here, continue.")
    
            except:
                type, value, tb = sys.exc_info()
                self.textbrowser_logging.append("Something went wrong when parsing a library: %s" % (value.message))
                traceback.print_exception(type, value, tb, limit=10, file=sys.stdout)
                self.textbrowser_logging.append("If MSSQL, are the access credentials right? Did you set the right permissions on the DB? Did you actually create a DB on mssql or sqlite?")
        else:
            self.textbrowser_logging.append("Connect to a DB!")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = DiffRay_Main()
    window.show()
    app.exec_()