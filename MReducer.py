# -*- coding: utf-8 -*-

import sys

from PySide.QtCore import *
from PySide.QtGui import *

from yelib.qt.layout import *
from yelib.qt.widgets import *
from yelib.task import *

from MainArea import MainArea

STYLE_SHEET = """
/*
QTabBar::tab,
*/
QPushButton {
    border: 1px outset rgb(150,150,150);
    border-radius: 3px;
}
QPushButton:hover {
    border: 1.5px outset dimgray;
    background: rgb(150,150,150);
}
QPushButton:pressed {
    border: 1.5px outset dimgray;
    background: rgb(180,180,180);
}
#btn-start {
	background-color:#4d90fe;
	/*background-color:#c53727;*/
	color: rgb(240, 240, 230);
	font-weight: bold;
}
#btn-start:hover {
	background-color:#509fff;
}
#btn-start:pressed {
	background-color:#4080f0;
}
QMessageBox QPushButton {
	width: 50px;
	height: 25px;
}
/*
QTabBar::tab:hover { background: rgb(150,150,150); }
QTabBar::tab:selected {
    color: rgb(220,220,220);
    background: rgb(130,130,130);
    border: 1px inset rgb(150,150,150);
}
QTabWidget::pane { border:1px solid rgb(150,150,150);}
*/
QStatusBar::item { border:0; }
QLineEdit, QTextEdit, QComboBox,
QListWidget, QTableWidget, QGroupBox {
    padding: 2px; border-radius: 3px;
    border:1px solid rgb(150,150,150);
}
QLineEdit:focus, QTextEdit:focus {
    border:1.5px solid goldenrod;
}
QGroupBox{ margin-top: 5px; }
QGroupBox::title { left: 10px; top: -5px; }
QListWidget, QTableWidget { padding: 0; }
QListWidget::item { margin:2px; }
QListWidget::item QLineEdit:focus { border:0; border-radius:0; margin:0; padding:0; }
QHeaderView::section {
    padding: 3px;
    border: 1px solid rgb(150,150,150);
    font-size: 12px;
    background-color: lightblue;
}
QTextBrowser {
    color: white;
    /* background:lightyellow; */
    background: rgb(50,50,50);
    padding: 5px; border: 0;
}
IconLabel { border:0; }
/*
IconLabel:hover { background:none; }
*/
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setMinimumHeight(600)
        self.main = MainArea(self)
        self.setCentralWidget(self.main)

        self.setWindowTitle(u'Movie Reducer')
        self.setWindowIcon(QIcon('image/logo.png'))
        self.setStyleSheet(STYLE_SHEET)
        #self.btnPath.clicked.connect(self.select_path)


    def closeEvent(self, event):
        #self.dlgSettings.saveConfig()
        self.main.close()
        event.accept()

    def get_root_path(self):
        return self.main.txtPath.text()

    def center(self):
        self.move(
            QApplication.desktop().screen().rect().center() -
            self.rect().center() )

    def showLoading(self, msg, loading=True):
        self.lbLoadingText.setText(msg)
        #self.statusBar().showMessage(msg)
        self.lbLoadingGif.setVisible(loading)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.center()
    sys.exit(app.exec_())

