#!python3
# -*- coding: utf-8 -*-
# this script demostrates how to use PyMuPDF in multiprocessing to avoid unresponsive GUI when fitz.open costs a long time
#yinkaisheng@live.com
import os
import sys
import time
import multiprocessing as multiprcs
import queue
import fitz
from PyQt5 import QtCore, QtGui, QtWidgets
import PDFSearcher

class DocForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.currentProcess = None
        self.queue = multiprcs.Queue()
        self.docBeingProcessedInQueue = multiprcs.Queue()
        self.totalPageCount = 0
        self.currentPageNr = 0
        self.lastDir = ''
        #This timer sends the next page to the timer when it times out
        self.timerSend = QtCore.QTimer(self)
        self.timerSend.timeout.connect(self.onTimerSendPageNum)
        #This timer displays a page if a new page is available
        self.timerGet = QtCore.QTimer(self)
        self.timerGet.timeout.connect(self.onTimerGetPage)
        #this timer displays
        self.timerWaiting = QtCore.QTimer(self)
        self.timerWaiting.timeout.connect(self.onTimerWaiting)

    #Function starts on main thread and sends avtual opening of the PDF to thread
    def startDocRender(self, path):
        # path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Document", self.lastDir,
        #             "All Supported Files (*.pdf;*.epub;*.xps;*.oxps;*.cbz;*.fb2);;PDF Files (*.pdf);;EPUB Files (*.epub);;XPS Files (*.xps);;OpenXPS Files (*.oxps);;CBZ Files (*.cbz);;FB2 Files (*.fb2)", options=QtWidgets.QFileDialog.Options())
        if path:
            self.lastDir, self.file = os.path.split(path)
            if self.currentProcess:
                self.queue.put(-1) # use -1 to notify the process to exit
            self.timerSend.stop()
            self.currentPageNr = 0
            self.totalPageCount = 0
            #Starts a process for the function instead of calling the function
            #Set the process
            self.currentProcess = multiprcs.Process(target=openDocInProcess, args=(path, self.queue, self.docBeingProcessedInQueue))
            #Start the process
            self.currentProcess.start()

            self.timerGet.start(40)
            self.label.setText('0/0')
            #Put the started process actually in the queue
            self.queue.put(0)
            self.startTime = time.perf_counter()
            self.timerWaiting.start(40)

    def playDoc(self):
        self.timerSend.start(500)

    def stopPlay(self):
        self.timerSend.stop()

    def onTimerSendPageNum(self):
        '''called when the send timer times out.'''
        if self.currentPageNr < self.totalPageCount - 1:
            #Send the next page to the queue
            self.queue.put(self.currentPageNr + 1)
        else:
            self.timerSend.stop()

    def onTimerGetPage(self):
        '''Called by timeout of timerget. Probably the opening the doc is in a thread. An external timer tries to grab a page and display it everytime a page has come available'''
        try:
            #Returns item if available
            pageData = self.docBeingProcessedInQueue.get(False)
            if isinstance(pageData, int):
                #If docdata is an int instead of list of properties
                #This int is the page number.
                self.timerWaiting.stop()
                self.totalPageCount = pageData
                #Set the label that the document is loading
                self.label.setText('{}/{}'.format(self.currentPageNr + 1, self.totalPageCount))
            else:#tuple, pixmap info
                pageNum, samples, width, height, stride, alpha = pageData
                self.currentPageNr = pageNum
                self.label.setText('{}/{}'.format(self.currentPageNr + 1, self.totalPageCount))
                colorCodingFormat = QtGui.QImage.Format_RGBA8888 if alpha else QtGui.QImage.Format_RGB888
                qtImage = QtGui.QImage(samples, width, height, stride, colorCodingFormat)
                PDFSearcher.
        except queue.Empty as ex:
            #Else it waits
            pass

    def onTimerWaiting(self):
        self.labelImg.setText('Loading "{}", {:.2f}s'.format(self.file, time.perf_counter() - self.startTime))

    def closeEvent(self, event):
        self.queue.put(-1)
        event.accept()

def openDocInProcess(path, queNum, quePageInfo):
    '''Process sent to the queue for opening the dock'''
    start = time.perf_counter()
    doc = fitz.open(path)
    end = time.perf_counter()

    #it somehow gets this from the multiprocessing queue? and puts pagecount to it.
    quePageInfo.put(doc.pageCount)

    #continuous because it's in a thread
    while True:
        num = queNum.get()
        if num < 0:
            break
        page = doc.loadPage(num)
        pix = page.getPixmap()
        quePageInfo.put((num, pix.samples, pix.width, pix.height, pix.stride, pix.alpha))
    doc.close()
    print('process exit')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = DocForm()
    sys.exit(app.exec_())