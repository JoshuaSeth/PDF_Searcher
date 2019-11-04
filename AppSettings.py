import sys
from PyQt5.QtWidgets import QWidget, QAction, qApp, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow, QLabel, QGridLayout, QSpinBox
from PyQt5.QtGui import QIcon
import re

class SettingsMenu():

    documentShowColumns = 2
    documentShowRows = 2


    def __init__(self):
        super().__init__()

        self.LoadSettings()

        self.title = "Search Multiple PDFs"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300

        self.initUI()

    def initUI(self):
        self._new_window = NewWindow()
        self._new_window.settingsMenu = self
        self._new_window.__init__()
        self._new_window.load()
        self._new_window.show()

        print('loaded preferences')

    def SaveSettings(self):
        with open('settings.txt', 'w') as filehandle:
            filehandle.write("DocumentShowColumns ")
            filehandle.write(str(self.documentShowColumns) + " ")
            filehandle.write("DocumentShowRows ")
            filehandle.write(str(self.documentShowRows) + " ")

    def LoadSettings(self):
        with open('settings.txt', 'r') as filehandle:
            string = filehandle.read()
            f = string.split("DocumentShowColumns")[1].split(" ")[1]
            self.documentShowColumns = int(f)
            f = string.split("DocumentShowRows")[1].split(" ")[1]
            self.documentShowRows = int(f)



class NewWindow(QMainWindow):
    settingsMenu = None

    def __init__(self):
        super(NewWindow, self).__init__()

    def load(self):

        #Main layout
        self._new_window = None
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        self.mainContainer = QHBoxLayout()
        mainWidget.setLayout(self.mainContainer)

        # Buttons
        buttonsContainer = QVBoxLayout()
        self.mainContainer.addLayout(buttonsContainer)

        self.showPagesOptions = QPushButton("Page Display")
        self.showPagesOptions.setToolTip('Page Display')
        self.showPagesOptions.clicked.connect(self.SetOptionsContent)
        buttonsContainer.addWidget(self.showPagesOptions)
        self.show()

    def SetOptionsContent(self):
        print('setting content')
        #Make a grid for the labels and the spinboxes
        fieldsContainer = QHBoxLayout()

        self.settingsMenu.LoadSettings()

        twoFields1 = QVBoxLayout()
        widthLabel = QLabel("Show Documents Columns")
        self.widthInput = QSpinBox()
        self.widthInput.setValue(self.settingsMenu.documentShowColumns)
        self.widthInput.valueChanged.connect(self.SetPagesValues)
        twoFields1.addWidget(widthLabel)
        twoFields1.addWidget(self.widthInput)


        twoFields2 = QVBoxLayout()
        heightLabel = QLabel("Show Documents Rows")
        self.heightInput = QSpinBox()
        self.heightInput.setValue(self.settingsMenu.documentShowRows)
        self.heightInput.valueChanged.connect(self.SetPagesValues)
        twoFields2.addWidget(heightLabel)
        twoFields2.addWidget(self.heightInput)

        fieldsContainer.addLayout(twoFields1)
        fieldsContainer.addLayout(twoFields2)

        self.mainContainer.addLayout(fieldsContainer)

        #add grid to maincontainer

    def SetPagesValues(self):
        self.settingsMenu.documentShowColumns = self.widthInput.value()
        self.settingsMenu.documentShowRows = self.heightInput.value()
        self.settingsMenu.SaveSettings()



if __name__ == '__main__':
    app = QApplication([])
    gui = SettingsMenu()
    gui.show()
    app.exec_()



