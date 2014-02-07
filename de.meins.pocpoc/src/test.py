'''
Created on 13.10.2013

@author: Marion
'''

from os import path
import sys
from PyQt4 import QtGui, QtCore



class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(600,500)
        self.setWindowTitle('WhatsMyTitle')
        self.textEdit = QtGui.QTextEdit()
        
        self.setCentralWidget(self.textEdit)
        
        exit = QtGui.QAction(QtGui.QIcon(path.join(path.abspath(path.dirname(__file__)), '..', 'icons', 'witch.png')), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        settings = QtGui.QAction(QtGui.QIcon(path.join(path.abspath(path.dirname(__file__)), '..', 'icons', 'cat.png')), 'Settings', self)
        settings.setShortcut('Ctrl+S')
        settings.setStatusTip('Modify Settings')
        
        signatures = QtGui.QAction(QtGui.QIcon(path.join(path.abspath(path.dirname(__file__)), '..', 'icons', 'ghost.png')), 'Signatures', self)
        signatures.setShortcut('Ctrl+U')
        signatures.setStatusTip('Update Signatures')
        self.connect(signatures, QtCore.SIGNAL('triggered()'), self.updateSigs)
        
        mappings = QtGui.QAction(QtGui.QIcon(path.join(path.abspath(path.dirname(__file__)), '..', 'icons', 'pumpkin.png')), 'Mappings', self)
        mappings.setShortcut('Ctrl+U')
        mappings.setStatusTip('Update Mappings')
        self.connect(mappings, QtCore.SIGNAL('triggered()'), self.updateMappings)
        
        
        self.toolbar = self.addToolBar('Stuff')
        self.toolbar.addAction(signatures)
        self.toolbar.addAction(mappings)

        menubar = self.menuBar()
        file = menubar.addMenu('&Program')
        file.addAction(settings)
        file.addAction(signatures)
        file.addAction(exit)
        
    def updateSigs(self):
        self.textEdit = QtGui.QTextEdit()
        ok = QtGui.QPushButton("OK")
        cancel = QtGui.QPushButton("Cancel")
        
        #self.setCentralWidget(self.textEdit)
        
        filename = path.join(path.abspath(path.dirname(__file__)), '..', 'conf', 'signatures.conf')
        file = open(filename)
        data = file.read()
        self.textEdit.setText(data)
        
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok)
        hbox.addWidget(cancel)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        grid.addWidget(self.textEdit, 1, 0)
        grid.addWidget(ok, 2, 0)
        grid.addWidget(cancel, 2, 1)

        self.setLayout(grid)

        #self.resize(300, 150)


    def updateMappings(self):
        #self.textEdit = QtGui.QTextEdit()
        self.setCentralWidget(self.textEdit)
        
        filename = path.join(path.abspath(path.dirname(__file__)), '..', 'conf', 'sig_mapping.conf')
        file = open(filename)
        data = file.read()
        self.textEdit.setText(data)


class SignatureWindow(QtGui.QWidget):
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.resize(300, 600)
        self.setWindowTitle('Signatures')
        
        self.textEdit = QtGui.QTextEdit()
        #self.setCentralWidget(self.textEdit)
        
        filename = path.join(path.abspath(path.dirname(__file__)), '..', 'conf', 'signatures.conf')
        file = open(filename)
        data = file.read()
        self.textEdit.setText(data)
        


if __name__ == '__main__':        
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())