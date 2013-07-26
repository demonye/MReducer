# -*- coding: utf-8 -*-

import os
from PySide.QtCore import *
from PySide.QtGui import *
from yelib.qt.layout import *

class FileSelector(yBoxLayout):
    textChanged = Signal(unicode)

    def __init__(self, label, title, filter="*.*", type="file"):

        self.txt = QLineEdit()
        self.title =  title
        self.filter = filter
        self.type = type
        self.btn = QPushButton(QIcon('image/file.png'), '')
        #self.btn.setStyleSheet("""
        #QPushButton { border:0; }
        #QPushButton:hover {
        #   border:1px outset dimgray;
        #   background:lightyellow;
        #}
        #""")
        self.btn.setFixedHeight(20)
        self.btn.clicked.connect(self.selectFile)
        self.txt.textChanged.connect(self.txtChanged)

        ltArr = []
        if label:
            ltArr.append(QLabel(label))
        ltArr += [ self.txt, self.btn ]

        ltData = [ ltArr ]
        super(FileSelector, self).__init__(ltData)
        #self.setLayout(lt)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
        #self.setContentsMargins(0,0,0,0)
        #self.setBaseSize(0, 0)
        #self.setStyleSheet("margin:0px;padding:0px")

    def text(self):
        return self.txt.text()
    def setText(self, text):
        return self.txt.setText(text)

    def selectFile(self):
        if self.type == "file":
            fname,_ = QFileDialog.getOpenFileName(None,
                    self.title, self.text(), self.filter)
            self.txt.setText(fname.replace('/', os.sep))
        elif self.type == "files":
            fnames,_ = QFileDialog.getOpenFileNames(None,
                    self.title, self.text(), self.filter)
            self.txt.setText('"' + '","'.join(
                [fn.replace('/', os.sep) for fn in fnames]) + '"')
        elif self.type == "dir":
            fname = QFileDialog.getExistingDirectory(None,
                    self.title, self.text())
            if len(fname) > 0:
                self.txt.setText(fname)

    def txtChanged(self, path):
        self.textChanged.emit(path)


class IconLabel(QPushButton):
    def __init__(self, icon, text, parent=None):
        super(IconLabel, self).__init__(icon, text, parent)
        self.setStyleSheet("""
        IconLabel { border:0; }
        IconLabel:hover { background:none; }
        """)

