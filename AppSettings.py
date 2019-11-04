import sys
from PyQt5.QtWidgets import QWidget, QAction, qApp, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow, QLabel
from PyQt5.QtGui import QIcon


class SettingsMenu(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = "Search Multiple PDFs"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300

        self.initUI()

    def initUI(self):
        #Main layout

        self._new_window = NewWindow()
        self._new_window.__init__()
        self._new_window.show()

        print('loaded preferences')


class NewWindow(QMainWindow):
    def __init__(self):
        super(NewWindow, self).__init__()
        self._new_window = None
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        mainContainer = QHBoxLayout()
        mainWidget.setLayout(mainContainer)

        # Buttons
        buttonsContainer = QVBoxLayout()
        mainContainer.addLayout(buttonsContainer)

        self.startSearchButton = QPushButton("Page Display")
        self.startSearchButton.setToolTip('Page Display')
        # self.startSearchButton.clicked.connect(self.RunProgram)
        buttonsContainer.addWidget(self.startSearchButton)
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    gui = NewWindow()
    gui.show()
    app.exec_()

