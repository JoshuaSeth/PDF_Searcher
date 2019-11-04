import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon


class ShowMenuItems():

    def __init__(self, mainWindow):
        super().__init__()

        self.initUI(mainWindow)

    def initUI(self, mainWindow):
        exitAct = QAction(QIcon('exit.png'), ' &Exit', mainWindow)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        #mainWindow.statusBar()

        menubar = mainWindow.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Edit')
        fileMenu.addAction(exitAct)




