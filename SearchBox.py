
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QScrollArea, QWidget, QVBoxLayout, QProgressBar, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QApplication, QCheckBox, QGridLayout, QGroupBox, QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QDockWidget, QTabBar
import sys


class SearchBox():

    searchfields = []


    #Use this group for keyword combinations
    def __init__(self):
        self.groupBox = QGroupBox("Search Terms")

        #One initial search field
        self.searchTerm1 = QLineEdit("Example Search Term")
        self.searchfields.append(self.searchTerm1)

        #Add it to a vbox
        self.row = QHBoxLayout()
        self.row.addWidget(self.searchTerm1)

        #Add the vbox to a container
        self.row.addStretch(1)
        self.groupBox.setLayout(self.row)

        #Create button for creating more search fields
        self.addButton = QPushButton("+")
        self.addButton.clicked.connect(lambda: self.AddSearchField())
        self.row.addWidget(self.addButton)

    def AddSearchField(self):
        self.nextST = QLineEdit("Example Search Term")
        self.searchfields.append(self.nextST)

        self.addLabel = QLabel("&")

        self.row.addWidget(self.addLabel)
        self.row.addWidget(self.nextST)
        self.row.removeWidget(self.addButton)
        self.row.addWidget(self.addButton)
        self.groupBox.setLayout(self.row)

        print("added sf")

    def Get(self):
        return self.groupBox

