# -*- coding: utf-8 -*-

from PySide.QtCore import *
from PySide.QtGui import *

from yelib.qt.layout import *
from yelib.qt.widgets import *
from yelib.task import *

import json
import os.path
import re
import math
import threading


FULLPATH = 1
RUNSTATE = 2
WORKER = 3

STATE_INIT = 0
STATE_WAITING = 1
STATE_RUNNING  = 2
STATE_DONE = 3
STATE_STOPPING = 4
STATE_STOPPED = 5


class ProgressDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ProgressDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 2:
            progress = int(index.data())
            pOption = QStyleOptionProgressBarV2()
            r = option.rect
            pOption.rect = r
            pOption.rect.setTop(r.top()+5)
            pOption.rect.setHeight(r.height()-10)
            pOption.minimum = 0
            pOption.maximum = 100
            pOption.progress = progress
            pOption.text = str(progress) + '%'
            pOption.textAlignment = Qt.AlignCenter
            pOption.textVisible = True
            QApplication.style().drawControl(QStyle.CE_ProgressBar, pOption, painter)
        #elif index.column() == 2:
        #    status = index.data()
        #    pOption = QStyleOptionViewItemV4()
        #    #pOption.displayAlignment = Qt.AlignCenter
        #    pOption.text = ""
        #    print status
        #    if status == "init":
        #        #pOption.widget = None
        #        pOption.icon = QIcon('image/target.png')
        #    elif status == "running":
        #        #pOption.widget = self.createLoadingGif()
        #        pOption.icon = QIcon('')
        #    elif status == "done":
        #        #pOption.widget = None
        #        pOption.icon = QIcon('image/checkmark2.png')
        #    QApplication.style().drawControl(QStyle.CE_ItemViewItem, pOption, painter)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

def ic(name):
    return QIcon('image/{}.png'.format(name))

def cpu_count():
    import multiprocessing
    return multiprocessing.cpu_count()

class MainArea(QWidget):
    def __init__(self, parent=None):
        super(MainArea, self).__init__(parent)

        self.txtPath = FileSelector(u'Select movie(s)', u'Select movie(s)', type='file')

        pb = QPushButton
        buttons = (
                ('btnAdd', pb(ic('add'), u'Add'), self.addFiles),
                ('btnRemove', pb(ic('delete'), u'Remove'), self.removeFiles),
                ('btnAll', pb(ic('check'), u'All'), self.selectAll),
                ('btnNone', pb(u'None'), self.selectNone),
                ('btnStart', pb(u'Start'), self.startConvert),
                ('btnStop', pb(ic('cancel'), u'Stop'), self.stopConvert),
                )
        for btn in buttons:
            setattr(self, btn[0], btn[1])
            btn[1].setFixedSize(80, 28)
            btn[1].clicked.connect(btn[2])
        self.btnStart.setObjectName('btn-start')
        self.btnStart.setFixedSize(80, 28)
        self.bigFirst = QCheckBox(u'Big file first')
        self.bigFirst.setCheckState(Qt.Checked)

        grpLst = QGroupBox(u'Movie list')
        #u"<div style='font:bold 14px arial;color:#c53727'>Movie List</div>"
        ltLst = yBoxLayout([
            [ self.tb ],
            [ self.btnAdd, self.btnRemove, self.btnAll, self.btnNone, None,
                self.btnStart, self.btnStop ]
        ])
        grpLst.setLayout(ltLst)
        grpOpt = QGroupBox(u'Options')
        ltOpt = yBoxLayout([
            [ u'Output quality', self.slider, None, self.bigFirst, None,
              u'Reduce', self.spin, u'movie(s) one time', None ],
        ])
        grpOpt.setLayout(ltOpt)
        self.layout = yBoxLayout([
            [ grpOpt ],
            [ grpLst ],
        ])
        self.setLayout(self.layout)
        #self.workers = [ TaskWorker() ] * 4
        self.files = set()
        self.nRunning = 0
        self.lock = threading.Lock()
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.convertMovies)
        self.timer.start()

    @property
    def tb(self):
        try:
            _ = self._tb
        except AttributeError:
            tb = QTableWidget()
            tb.setMinimumWidth(600)
            tb.setMinimumHeight(400)
            columns = ('', '', u"Progress", u"Filename", u"Size(MB)", u"Folder")
            tb.setColumnCount(len(columns))
            tb.setSelectionBehavior(QAbstractItemView.SelectRows)
            tb.setEditTriggers(QAbstractItemView.NoEditTriggers)
            #myHeader = MyHeader(Qt.Horizontal, self)
            #tb.setHorizontalHeader(myHeader)
            tb.setHorizontalHeaderLabels(columns)

            header = tb.horizontalHeader()
            header.setResizeMode(0, QHeaderView.Fixed)
            header.resizeSection(0, 20) 
            header.setResizeMode(1, QHeaderView.Fixed)
            header.resizeSection(1, 26) 
            #header.setResizeMode(2, QHeaderView.Fixed)
            header.resizeSection(2, 85) 
            #header.setResizeMode(3, QHeaderView.ResizeToContents)
            header.resizeSection(3, 200) 
            header.setResizeMode(4, QHeaderView.ResizeToContents)
            header.setResizeMode(5, QHeaderView.Stretch)
            tb.verticalHeader().hide()
            tb.setAlternatingRowColors(True)
            tb.setItemDelegate(ProgressDelegate())
            self._tb = tb

        return self._tb

    @property
    def slider(self):
        try:
            _ = self._slider
        except AttributeError:
            slider = QSlider(Qt.Horizontal)
            slider.setFixedWidth(80)
            slider.setTickInterval(1)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setMaximum(4)
            #slider.setMinimum(0)
            slider.setValue(2)
            self._slider = slider

        return self._slider

    @property
    def spin(self):
        try:
            _ = self._spin
        except AttributeError:
            spin = QSpinBox()
            spin.setFixedWidth(40)
            spin.setRange(1, cpu_count())
            spin.setValue((1+cpu_count())/2)
            self._spin = spin

        return self._spin

    @property
    def loading(self):
        loading = QLabel()
        loading.hide()
        movie = QMovie("image/loading.gif")
        movie.start()
        loading.setMovie(movie)
        return loading

    def sourceChanged(self, pullpath):
        srcpath, srcfile = os.path.split(pullpath)
        fname, ext = os.path.splitext(srcfile)
        self.txtOutPath.setText(os.path.join(srcpath, fname+"-out"+ext))

    def addFiles(self):
        fnames,_ = QFileDialog.getOpenFileNames(
                None, u'Select movie(s)', u'', u'*.*')
        tb = self.tb
        i = 0
        for fn in fnames:
            if fn in self.files:
                continue
            tb.insertRow(i)
            chk = QTableWidgetItem()
            chk.setCheckState(Qt.Checked)
            chk.setData(FULLPATH, fn)
            chk.setData(RUNSTATE, STATE_INIT)
            tb.setItem(i, 0, chk)
            prg = QTableWidgetItem()
            tb.setItem(i, 1, QTableWidgetItem())
            tb.setItem(i, 2, QTableWidgetItem('0'))
            path, fname = os.path.split(fn)
            tb.setItem(i, 3, QTableWidgetItem(fname))
            fs = os.path.getsize(fn)
            fs = math.floor(fs*100/(1024*1024) + 0.5) / 100
            tb.setItem(i, 4, QTableWidgetItem(str(fs)))
            pathItem = QTableWidgetItem(path)
            pathItem.setToolTip(path)
            tb.setItem(i, 5, pathItem)
            self.files.add(fn)
            i += 1

    def removeFiles(self):
        tb = self.tb
        for i in xrange(tb.rowCount()-1,-1,-1):
            if tb.item(i, 0).checkState() == Qt.Checked:
                self.files.remove(self.role(i, FULLPATH))
                tb.removeRow(i)

    def selectAll(self):
        tb = self.tb
        for i in xrange(tb.rowCount()):
            tb.item(i, 0).setCheckState(Qt.Checked)
    def selectNone(self):
        tb = self.tb
        for i in xrange(tb.rowCount()):
            tb.item(i, 0).setCheckState(Qt.Unchecked)

    def role(self, row, role, data=None):
        if data is None:
            return self.tb.item(row, 0).data(role)
        else:
            self.tb.item(row, 0).setData(role, data)

    def state(self, row, state=None, changeN=True):
        if state is None:
            return self.role(row, RUNSTATE)

        self.lock.acquire()
        tb = self.tb
        if state == STATE_DONE:
            tb.setItem(row, 1, QTableWidgetItem(ic('checkmark'), ''))
            tb.setCellWidget(row, 1, None)
            if changeN: self.nRunning -= 1
        elif state == STATE_STOPPED:
            tb.setItem(row, 1, QTableWidgetItem(ic('cross'), ''))
            tb.setCellWidget(row, 1, None)
            if changeN: self.nRunning -= 1
        elif state == STATE_WAITING:
            tb.setItem(row, 1, QTableWidgetItem(ic('hourglass'), ''))
            tb.setCellWidget(row, 1, None)
        elif state == STATE_RUNNING:
            tb.setItem(row, 1, None)
            tb.setCellWidget(row, 1, self.loading)
            if changeN: self.nRunning += 1
        elif state == STATE_STOPPING:
            tb.setItem(row, 1, QTableWidgetItem(ic('cross'), ''))
            tb.setCellWidget(row, 1, self.loading)
        else:
            tb.setItem(row, 1, None)
            tb.setCellWidget(row, 1, None)
        self.role(row, RUNSTATE, state)
        self.lock.release()

    def startConvert(self):
        tb = self.tb
        for i in xrange(tb.rowCount()):
            item = tb.item(i, 0)
            state = self.state(i)
            if item.checkState() == Qt.Checked and state in (STATE_INIT,STATE_STOPPED):
                self.state(i, STATE_WAITING)

    def _startConvert(self, row):
        if self.nRunning >= self.spin.value():
            return

        tb = self.tb
        progress = tb.item(row, 2)
        worker = TaskWorker()
        bitrate = 512 * (2**self.slider.value())
        end_code = 0

        def begin():
            progress.setText('0')
            self.role(row, WORKER, worker)
        def end():
            if self.state(row) == STATE_DONE:
                progress.setText('100')
            worker.stop()
            self.role(row, WORKER, None)
        def handler(msg):
            if msg.type == OutputType.OUTPUT:
                arr = re.findall(r"^Pos.*\((.*)%\).*$", msg.output)
                if len(arr) > 0: progress.setText(arr[0])
            if msg.type == OutputType.NOTIFY and msg.output.startswith('EXIT '):
                code = int(msg.output.split()[1])
                if code == 0:
                    self.state(row, STATE_DONE)
                else:
                    self.state(row, STATE_STOPPED)

        self.state(row, STATE_RUNNING)

        # mencoder 1.avi -o 2.avi -oac mp3lame -ovc xvid -xvidencopts bitrate=1024
        infile = self.role(row, FULLPATH)
        path, fn = os.path.split(infile)
        outfile = os.path.join(path, "-cmd-" + fn)
        task = Task(CmdTask([os.path.join("bin", "mencoder"),
            infile.encode('gbk'), "-o", outfile.encode('gbk'),
            "-oac", "mp3lame", "-ovc", "xvid", "-xvidencopts",
            "bitrate={}".format(bitrate)
            ]))
        task.init(
                TaskHandler(begin), TaskHandler(end),
                TaskHandler(handler)
                )
        worker.add_task(task)

    def stopConvert(self):
        tb = self.tb
        for i in xrange(tb.rowCount()):
            item = tb.item(i, 0)
            state = self.state(i)
            if item.checkState() == Qt.Checked and state in (STATE_WAITING,STATE_RUNNING):
                self.state(i, STATE_STOPPING)

    def _stopConvert(self, row):
        worker = self.role(row, WORKER)
        if worker:
            worker.stop()
        else:
            self.state(row, STATE_STOPPED, False)

    def convertMovies(self):
        tb = self.tb
        row = -1
        maxSize = 0
        for i in xrange(tb.rowCount()):
            state = self.state(i)
            fs = float(tb.item(i, 4).text())
            if state == STATE_WAITING:
                #self._startConvert(i)
                if self.bigFirst.checkState() == Qt.Checked:
                    if fs > maxSize:
                        row = i
                        maxSize = fs
                else:
                    row = i
                    break
            elif state == STATE_STOPPING:
                self._stopConvert(i)
        if row >= 0:
            self._startConvert(row)

    def closeEvent(self, event):
        #for wk in self.workers:
        #    wk.stop()
        self.timer.stop()
        event.accept()
