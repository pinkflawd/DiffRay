'''
Created on 08.03.2014

@author: Marion
'''

import os
import sys

from PyQt4 import QtGui, QtCore, uic


class InfoBox(QtGui.QDialog):

    def __init__(self, parent=None):
        super(InfoBox, self).__init__(parent)
        self.ui = uic.loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'ui', 'infobox.ui'), self)
        
        self.textEdit_output = self.ui.textEdit_output
        
        self.button_ok = self.ui.button_ok
        self.connect(self.button_ok, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))
