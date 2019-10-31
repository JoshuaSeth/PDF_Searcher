import os
import subprocess
from PyPDF2 import PdfFileWriter, PdfFileReader
import PyPDF2
import re





def Read(fileString, saveCount, searchTerms, dirString):
    # open the pdf file
    openedPDF = PyPDF2.PdfFileReader(fileString)

    if not openedPDF.isEncrypted:
        SearchPDFPages(dirString, fileString, openedPDF, saveCount, searchTerms)



def SearchPDFPages(dirString, fileString, openedPDF, saveCount, searchTerms):
    # get number of pages
    NumPages = openedPDF.getNumPages()
    savedPages = []
    totalText = ""
    # extract text and do the search
    for i in range(0, NumPages):
        PageObj = openedPDF.getPage(i)
        print("this is page " + str(i))
        Text = PageObj.extractText()
        totalText += Text
        # print(Text)
        for word in searchTerms:
            ResSearch = re.search(word, Text)
            if (ResSearch != None):
                print("Found")
                savedPages.append(i)
    saveCount += 1
    SavePDFPagesAsFile(fileString, savedPages, saveCount, dirString)


# def Print_Summary(Text):
    # # Object of automatic summarization.
    # auto_abstractor = AutoAbstractor()
    # # Set tokenizer.
    # auto_abstractor.tokenizable_doc = SimpleTokenizer()
    # # Set delimiter for making a list of sentence.
    # auto_abstractor.delimiter_list = [".", "\n"]
    # # Object of abstracting and filtering document.
    # abstractable_doc = TopNRankAbstractor()
    # # Summarize document.
    # result_dict = auto_abstractor.summarize(Text, abstractable_doc)
    # # Output result.
    # for sentence in result_dict["summarize_result"]:
    #     print(sentence)


def SavePDFPagesAsFile(fileString, pages, saveCount, dirString):
    print("Found")
    inputpdf = PdfFileReader(open(fileString, "rb"))
    output = PdfFileWriter()
    donePages = []


    for page in pages:
        for plusandminus in range(-3, 3):
            if not donePages.__contains__(page+plusandminus) and page+plusandminus > 0 and page+plusandminus < inputpdf.numPages:
                donePages.append(page+plusandminus)
                output.addPage(inputpdf.getPage(page+plusandminus))

    if not os.path.exists(dirString  + "/SearchResults/"):
        os.makedirs(dirString  + "/SearchResults/")
    srDir= dirString  + "/SearchResults/" +"result"+ str(saveCount) + "searchResult.pdf"
    with open(srDir, "wb") as outputStream:
        output.write(outputStream)
    subprocess.Popen([srDir],shell=True)







#GUI
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QApplication, QCheckBox, QGridLayout, QGroupBox, QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget
import sys

class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)
    directory = ""
    dirString = ""
    searchTerms = []
    currentBookNr = 0

    def run(self):
        for file in os.listdir(self.directory):
            self.currentBookNr += 1
            print(self.currentBookNr)
            filename = os.fsdecode(file)
            if filename.endswith(".pdf"):
                Read(self.dirString + "/" + filename, self.currentBookNr, searchTerms=self.searchTerms, dirString=self.dirString)
            self.countChanged.emit(self.currentBookNr)




class Window(QWidget):
    dirString = "/Users/"
    directory = os.fsencode(dirString)
    searchTerms = []

    def __init__(self):
        super().__init__()

        self.title = "Search Multiple PDFs"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300

        self.InitWindow()

    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainContainer = QHBoxLayout()

        vbox = QVBoxLayout()

        self.InstantiateDescription(vbox)
        self.InstantiateGetFolderPathButton(vbox)
        self.InstantiateSearchButton(vbox)
        self.InstantiateProgressBar(vbox)

        mainContainer.addLayout(vbox)


        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup(), 0, 0)
        grid.addWidget(self.createExampleGroup(), 1, 0)
        grid.addWidget(self.createExampleGroup(), 0, 1)
        grid.addWidget(self.createExampleGroup(), 1, 1)

        mainContainer.addLayout(grid)

        self.setLayout(mainContainer)

        self.show()

    def createExampleGroup(self):
        groupBox = QGroupBox("Search Terms")

        self.radio1 = QLineEdit("Zebedee")
        self.radio2 = QLineEdit("Beloved")
        self.radio3 = QLineEdit("Disciple")


        vbox = QVBoxLayout()
        vbox.addWidget(self.radio1)
        vbox.addWidget(self.radio2)
        vbox.addWidget(self.radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def InstantiateDescription(self, vbox):
        self.desc = QLabel("Select Folder a folder and press search. \nThe program will search all the PDFs in the folder for the search terms. \nIt creates a new folder in the search folder with all the search results.\n"
                           "For each PDF a new PDF is generated with the page with\nthe search result and the pages around it.")
        vbox.addWidget(self.desc)

    def InstantiateProgressBar(self, vbox):
        self.progbar = QProgressBar()
        self.progbar.setMaximum(100)
        vbox.addWidget(self.progbar)

    def InstantiateGetFolderPathButton(self, vbox):
        self.desc = QPushButton("Select Folder")
        self.desc.clicked.connect(self.getFolderPath)
        vbox.addWidget(self.desc)

    def InstantiateSearchButton(self, vbox):
        self.startSearchButton = QPushButton("Search")
        self.startSearchButton.setToolTip('This is an example button')
        self.startSearchButton.move(100, 70)
        self.startSearchButton.clicked.connect(self.RunProgram)
        vbox.addWidget(self.startSearchButton)

    def getFolderPath(self):

        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.dirString = str(folder)
        print(self.dirString)
        self.directory = os.fsencode(self.dirString)

    def RunProgram(self):
        self.searchTerms.append(self.radio1.text())
        self.searchTerms.append(self.radio2.text())
        self.searchTerms.append(self.radio3.text())
        print(self.directory)
        saveCount = 0
        path, dirs, files = next(os.walk(self.dirString))
        file_count = len(files)
        self.progbar.setMaximum(file_count)
        print(file_count)

        #Start multithreaded task
        self.PDFSearchTask = External()
        self.PDFSearchTask.directory = self.directory
        self.PDFSearchTask.dirString = self.dirString
        self.PDFSearchTask.searchTerms = self.searchTerms
        self.PDFSearchTask.currentBookNr = saveCount

        #Connect multithreaded counter
        self.PDFSearchTask.countChanged.connect(self.onCountChanged)
        self.PDFSearchTask.start()

    def onCountChanged(self, value):
        self.progbar.setValue(value)




App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
