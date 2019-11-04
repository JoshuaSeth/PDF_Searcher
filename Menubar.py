import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon
from AppSettings import SettingsMenu


class ShowMenuItems():

    def __init__(self, mainWindow):
        super().__init__()

        self.initUI(mainWindow)

    def initUI(self, mainWindow):

        openSettingsAct = QAction(QIcon('exit.png'), ' &Preferences', mainWindow)
        openSettingsAct.setShortcut('Ctrl+,')
        openSettingsAct.setStatusTip('Open preferences')
        openSettingsAct.triggered.connect(SettingsMenu)

        #mainWindow.statusBar()

        menubar = mainWindow.menuBar()
        fileMenu = menubar.addMenu('&File')
        optionsMenu = menubar.addMenu('&Edit')
        fileMenu.addAction(openSettingsAct)




