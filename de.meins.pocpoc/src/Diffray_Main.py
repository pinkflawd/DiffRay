'''
Created on 01.02.2014

@author: marschalek.m
'''

import logging.config
from optparse import OptionParser
import os
import re
from subprocess import Popen, CREATE_NEW_CONSOLE
import subprocess
import sys
import traceback

from PyQt4 import QtGui, QtCore, uic

import Database.MSSqlDB
import Database.SQLiteDB
import Diffing.Info
import Gui.Settings
import Gui.InfoBox
import Parsing.Library


class DiffRay_Main(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(DiffRay_Main, self).__init__(parent)
        self.main_ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'ui', 'diffray_main.ui'), self)
        
        # DATABASE INIT
        self.db = None
        self.backend = ""
        
        # C
        
        self.button_generateidb = self.main_ui.button_generateidb
        self.button_generatec = self.main_ui.button_generatec
        
        self.lineedit_idb2c = self.main_ui.lineedit_idb2c
        self.lineedit_idb2c.setText(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'IDB2C.exe'))
        self.lineedit_idb2c.setReadOnly(1)
        
        self.lineedit_asm2idb = self.main_ui.lineedit_asm2idb
        self.lineedit_asm2idb.setText(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'ASM2IDB.exe'))
        self.lineedit_asm2idb.setReadOnly(1)
                
        self.connect(self.button_generateidb, QtCore.SIGNAL('clicked()'), self.generateidb)    
        self.connect(self.button_generatec, QtCore.SIGNAL('clicked()'), self.generatec)    
         
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
        
        # DIFFING
        
        self.lineedit_lib1 = self.main_ui.lineedit_lib1
        self.lineedit_lib2 = self.main_ui.lineedit_lib2
        self.button_diff_id = self.main_ui.button_diff_id
        
        self.lineedit_pattern = self.main_ui.lineedit_pattern
        self.button_diff_name = self.main_ui.button_diff_name
        
        self.connect(self.button_diff_id, QtCore.SIGNAL('clicked()'), self.diff_id)
        self.connect(self.button_diff_name, QtCore.SIGNAL('clicked()'), self.diff_name)
        
        # INFO
        
        self.lineedit_searchlib = self.main_ui.lineedit_searchlib
        self.button_searchlib = self.main_ui.button_searchlib
        self.lineedit_allinfo = self.main_ui.lineedit_allinfo
        self.button_allinfo = self.main_ui.button_allinfo
        
        self.connect(self.button_searchlib, QtCore.SIGNAL('clicked()'), self.searchlib_mbox)
        self.connect(self.button_allinfo, QtCore.SIGNAL('clicked()'), self.allinfo_mbox)

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
        self.textbrowser_logging.append("DiffRay GUI v1.1 started - initial SQLite DB created in the data directory (dbdbdb.sqlite)")
        self.textbrowser_logging.append("The commanline version is available by starting the Main.py")
        self.textbrowser_logging.append("For more information and a (short) manual check out the project home on https://github.com/pinkflawd/DiffRay")
        
        
    ### SHOW INFO
        
    def searchlib_mbox(self):
        searchme = self.lineedit_searchlib.text().replace('\'','')
        if (searchme != "" and self.backend != ""):
            info = Diffing.Info.Info(self.backend)
            cursor = info.search_libs(searchme)
            
            libs = ""
            for item in cursor:
                name = item[1].replace('\\\\', '\\')
                libs += "%s | %s | Type %s | OS %s\n" % (item[0], name, item[3], item[2])
            
            box = Gui.InfoBox.InfoBox()
            box.textEdit_output.setText(libs)
            box.exec_()
            
        else:
            self.textbrowser_logging.append("Invalid lib search term or no connection to database!")
    
    def allinfo_mbox(self):
        libid = str(self.lineedit_allinfo.text())
        if (libid.isdigit() and self.backend != ""):
            info = Diffing.Info.Info(self.backend)
            cursor = info.library_info(libid)
            allinfo = "Libname;Functionname;Sigpattern;Line_Offset\n"  
            for item in cursor:
                allinfo += "%s;%s;%s;%s\n" % (item[0],item[1].replace('\\\\','\\'),item[2],item[3])

            box = Gui.InfoBox.InfoBox()
            box.textEdit_output.setText(allinfo)
            box.exec_()
            
        else:
            self.textbrowser_logging.append("Invalid lib ID or no connection to database!")    
               
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
        
        
    ### DATABASE STUFF    
        
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
       
    
    ### ACTION
            
    def generateidb(self):
        try:                        
            os.system(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'ASM2IDB.exe'))
        except:
            self.textbrowser_logging.append("IDB2C.exe is not where it should be! - put it into the util dir")
            
    def generatec(self):
        try:                        
            os.system(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'util', 'IDB2C.exe'))
        except:
            self.textbrowser_logging.append("ASM2IDB.exe is not where it should be! - put it into the util dir")    

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
                        os.system("start %s %s %s %s %s %s %s %s %s %s" % (cmd, diffray, '-d', path, '-t', ftype, '-o', opsys, '-b', self.backend))
                    elif os.path.exists(path):
                        os.system("start %s %s %s %s %s %s %s %s %s %s" % (cmd, diffray, '-p', path, '-t', ftype, '-o', opsys, '-b', self.backend))
                    else:
                        self.textbrowser_logging.append("Nothing to parse here. Maybe invalid path?")
                except:
                    self.textbrowser_logging.append("Something went wrong when parsing! Check if your input params are ok!")
                 
                else:
                    self.textbrowser_logging.append("Parsing %s" % path)
                        
            except:
                type, value, tb = sys.exc_info()
                self.textbrowser_logging.append("Something went wrong when parsing a library: %s" % (value.message))
                traceback.print_exception(type, value, tb, limit=10, file=sys.stdout)
                self.textbrowser_logging.append("If MSSQL, are the access credentials right? Did you set the right permissions on the DB? Did you actually create a DB on mssql or sqlite?")
        else:
            self.textbrowser_logging.append("Connect to a DB! OR python path wrong.")
            
    def diff_id(self):
        libid1 = str(self.lineedit_lib1.text())
        libid2 = str(self.lineedit_lib2.text())
        
        if (libid1.isdigit() and libid2.isdigit() and self.backend != ""):
            
            info = Diffing.Info.Info(self.backend)
            output = info.diff_twosided(libid1, libid2)
            
            box = Gui.InfoBox.InfoBox()
            box.textEdit_output.setText(output)
            box.exec_()
        
        else:
            self.textbrowser_logging.append("LibIDs wrong or no DB connection available.")
    
    def diff_name(self):
        sanilibname = str(self.lineedit_pattern.text().replace('\'', ''))
        
        if (sanilibname != "" and self.backend != ""):
            info = Diffing.Info.Info(self.backend)
            ids = info.search_libs_diffing(sanilibname)
            if (ids != -1):
                
                #info.diff_libs(ids[0],ids[1])   # 0.. Win7, 1.. Win8
                output = info.diff_twosided(ids[0],ids[1])
                
                box = Gui.InfoBox.InfoBox()
                box.textEdit_output.setText(output)
                box.exec_()
            
            else:
                self.textbrowser_logging.append("Pattern doesn't match a Win7/Win8 library pair.")
        
        else:
            self.textbrowser_logging.append("Libname pattern invalid or no DB connection available.")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = DiffRay_Main()
    window.show()
    app.exec_()