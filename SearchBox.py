
from PyQt5.QtWidgets import QColorDialog, QMainWindow, QApplication, QTabWidget, QScrollArea, QWidget, QVBoxLayout, QProgressBar, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QApplication, QCheckBox, QGridLayout, QGroupBox, QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QDockWidget, QTabBar
from PyQt5.QtCore import Qt
from colorPicker import LineEditColor
import sys


class SearchBox:
    searchFields = []
    program = None


    #Use this group for keyword combinations
    def __init__(self):
        self.groupBox = QGroupBox("or:")

        #One initial search field
        self.searchTerm1 = LineEditColor("Example")
        self.searchFields.append(self.searchTerm1)

        #Add it to a vbox
        self.row = QHBoxLayout()

        #Add the vbox to a container
        #self.row.addStretch(1)
        self.groupBox.setLayout(self.row)

        #Create button for creating more search fields
        self.addButton = QPushButton("+")
        self.addButton.clicked.connect(lambda: self.AddSearchField())
        self.row.addWidget(self.addButton)

        self.row.setAlignment(self.searchTerm1,Qt.AlignLeft)
        self.groupBox.setAlignment(Qt.AlignLeft)

    def AddSearchField(self):
        newST = LineEditColor("")
        self.searchFields.append(newST)

        self.addLabel = QLabel("&")

        self.addLabel.setFixedWidth(10)

        self.row.addWidget(self.addLabel, Qt.AlignLeft)
        self.row.addWidget(newST.colorPicker)
        self.row.addWidget(newST, Qt.AlignLeft)

        self.row.removeWidget(self.addButton)
        self.row.addWidget(self.addButton)







    def Get(self, title):
        self.groupBox.setTitle(title)
        return self.groupBox

