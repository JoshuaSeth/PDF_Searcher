#Program
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import PyPDF2
import re
import fitz

from SearchBox import SearchBox

#GUI
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QScrollArea, QWidget, QVBoxLayout, QProgressBar, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QApplication, QCheckBox, QGridLayout, QGroupBox, QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QDockWidget, QTabBar
import sys

from gensim.summarization.summarizer import summarize



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
        foundAll = True
        for word in searchTerms:
            ResSearch = re.search(word, Text)
            if (ResSearch is None):
                foundAll = False
        if foundAll:
            print("Found")
            savedPages.append(i)
    saveCount += 1
    SavePDFPagesAsFile(fileString, savedPages, saveCount, dirString, searchTerms)


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


def SavePDFPagesAsFile(fileString, pages, saveCount, dirString, searchTerms):
    if len(pages) is not 0:
        inputpdf = PdfFileReader(open(fileString, "rb"))
        output = PdfFileWriter()
        donePages = []

        # save pages with search results to a new pdf
        for page in pages:
            for plusandminus in range(-3, 3):
                if not donePages.__contains__(page+plusandminus) and page+plusandminus > 0 and page+plusandminus < inputpdf.numPages:
                    donePages.append(page+plusandminus)
                    output.addPage(inputpdf.getPage(page+plusandminus))

        #make directory and write to it
        if not os.path.exists(dirString  + "/SearchResults/"):
            os.makedirs(dirString  + "/SearchResults/")
        srDir= dirString  + "/SearchResults/" +"result"+ str(saveCount) + "searchResult.pdf"
        with open(srDir, "wb") as outputStream:
            output.write(outputStream)

        PrintSummaryOfResults(srDir=srDir, searchTerms=searchTerms)

def PrintSummaryOfResults(srDir, searchTerms):
    searchResultsPDF = PyPDF2.PdfFileReader(srDir)
    NumPages = searchResultsPDF.getNumPages()
    text = ""
    # extract text and do the search
    for i in range(0, NumPages):
        PageObj = searchResultsPDF.getPage(i)
        print("this is page " + str(i))
        pageText = PageObj.extractText()
        text += pageText
    title = ""
    for term in searchTerms:
        title += term + " "
    print(summarize(text=text, word_count=400))



#GUI
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




class Window(QMainWindow):
    dirString = "/Users/"
    directory = os.fsencode(dirString)
    searchTerms = []
    renderedPDFS = []
    pdfLayer1DocLimit = 4
    pdfLayer2DocLimit = 4
    currentDocsPDFLayer1 =0
    currentDocsPDFLayer2 = 0

    searchTermBoxes = []

    def __init__(self):
        super().__init__()

        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        layout = QVBoxLayout()
        mainWidget.setLayout(layout)

        self.title = "Search Multiple PDFs"
        mainWidget.top = 200
        mainWidget.left = 500
        mainWidget.width = 400
        mainWidget.height = 300

        self.InitWindow(layout)

    def InitWindow(self, layout):
        #General GUI Settings
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        #self.setGeometry(self.left, self.top, self.width, self.height)

        #fullWindowContainer = QVBoxLayout()

        uiContainer = QHBoxLayout()

        #Buttons GUI
        buttonsContainer = QVBoxLayout()

        #self.InstantiateDescription(buttonsContainer)
        self.InstantiateGetFolderPathButton(buttonsContainer)
        self.InstantiateSearchButton(buttonsContainer)
        self.InstantiateProgressBar(buttonsContainer)
        self.AddDockTest(buttonsContainer)
        uiContainer.addLayout(buttonsContainer)

        #Search term grid GUI
        self.searchTermsUI = QVBoxLayout()
        self.SearchTermsGrid = QVBoxLayout()
        self.searchTermsUI.addLayout(self.SearchTermsGrid)
        self.AddSearchBox("Search for:")
        uiContainer.addLayout(self.searchTermsUI)

        #Add setch line
        self.addSearchFieldButton = QPushButton("+")
        self.searchTermsUI.addWidget(self.addSearchFieldButton)
        self.addSearchFieldButton.clicked.connect(lambda: self.AddSearchBox("or:"))



        # PDF GUI
        self.pdfLayer1 = QHBoxLayout()
        self.pdfLayer2 = QHBoxLayout()

        #Add layers to super container

        layout.addLayout(uiContainer)
        layout.addLayout(self.pdfLayer1)
        layout.addLayout(self.pdfLayer2)
        #self.setLayout(mainWidget)

        self.show()

    def AddSearchBox(self, title):
        sb = SearchBox()
        self.SearchTermsGrid.addWidget(sb.Get(title))
        self.searchTermBoxes.append(sb)


    def AddDockTest(self, vbox):
        self._tabOptions = QTabWidget(self)
        self._tabOptions.setLayoutDirection(Qt.LeftToRight)
        self._tabOptions.setDocumentMode(False)
        self._tabOptions.setTabsClosable(False)
        self._tabOptions.setMovable(False)

        self.dock = QDockWidget('Tab Options', self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self._tabOptions)
        vbox.addWidget(self.progbar)


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
        self.startSearchButton.move(100, 70)
        self.startSearchButton.clicked.connect(self.RunProgram)
        vbox.addWidget(self.startSearchButton)

    def InstantiateScrollArea(self, box, PDFPath, PDFName):
        #Make directory for images of PDF
        imagesPath = os.getcwd() + "/PDFImages/" + PDFName +"/"
        if not os.path.exists(imagesPath):
            os.makedirs(imagesPath)

        #Prapre container to add images to and scrollarea
        scrollArea = QScrollArea(widgetResizable=True)
        content_widget = QWidget()
        scrollArea.setWidget(content_widget)
        imagesHolder = QVBoxLayout(content_widget)


        #Convert PDF to JPGs
        pdffile = PDFPath
        doc = fitz.open(pdffile)
        pageCount = PyPDF2.PdfFileReader(PDFPath).numPages
        for pageNR in range(0, pageCount):
            #If an image is not yet generated for a page generate it
            output = imagesPath + PDFName + "SRPage" + str(pageNR) + ".png"
            if not os.path.isfile(output):
                page = doc.loadPage(pageNR)  # number of page
                pix = page.getPixmap()
                pix.writePNG(output)

            #Actual images
            imageLabel = QLabel(self)
            pixmap = QPixmap(output)
            imageLabel.setPixmap(pixmap)
            #imageLabel.setMinimumHeight(pixmap.height())

            imagesHolder.addWidget(imageLabel)
            imageLabel.height = pixmap.height()


        box.addWidget(scrollArea)

    def CheckPDFAdddedByThread(self):
        # make directory and write to it
        if not os.path.exists(self.dirString + "/SearchResults/"):
            os.makedirs(self.dirString + "/SearchResults/")

        #Loop through search results directory
        dirName =self.dirString + "/SearchResults/"
        searchResultsDir = os.listdir(dirName)
        pathNU, dirsNU, files = next(os.walk(dirName))
        print(len(files))
        if len(files) is not 0:
            for searchResult in searchResultsDir:
                filename = os.fsdecode(searchResult)
                filePath = dirName+filename
                if not self.renderedPDFS.__contains__(filename) and filename.__contains__(".pdf"):
                    layer = self.pdfLayer1
                    if self.currentDocsPDFLayer1<self.pdfLayer1DocLimit:
                        self.currentDocsPDFLayer1+=1
                    if self.currentDocsPDFLayer1 >= self.pdfLayer1DocLimit:
                        self.currentDocsPDFLayer2 += 1
                        layer = self.pdfLayer2
                    self.InstantiateScrollArea(layer, filePath, filename)
                    self.renderedPDFS.append(filename)



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
        self.CheckPDFAdddedByThread()




App = QApplication(sys.argv)
window = Window()
from Menubar import ShowMenuItems
menu = ShowMenuItems(mainWindow=window)
#menu.__init__()
sys.exit(App.exec())