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

import AppSettings

App = []

class RenderPDFContainer:
    id = None
    pdf = None
    scrollAreaImagesHolder= None
    x=None
    y =None

    def doesContain(self, ipdf):
        if self.pdf is ipdf:
            return True
        else:
            return False



def Read(fileString, saveCount, searchTerms, dirString, filename):
    # open the pdf file
    openedPDF = PyPDF2.PdfFileReader(fileString)

    if not openedPDF.isEncrypted:
        SearchPDFPages(dirString, fileString, openedPDF, saveCount, searchTerms, filename)



def SearchPDFPages(dirString, fileString, openedPDF, saveCount, searchTermsLines, filename):
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
        lineCount = 0
        for line in searchTermsLines:
            foundAll = True
            for field in line:
                ResSearch = re.search(field.text(), Text)
                if (ResSearch is None):
                    foundAll = False
            if foundAll:
                print("Found all terms for line " + str(lineCount))
                savedPages.append(i)
            lineCount+=1
    saveCount += 1
    SavePDFPagesAsFile(fileString, savedPages, saveCount, dirString, searchTermsLines, filename)


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


def SavePDFPagesAsFile(fileString, pages, saveCount, dirString, searchTerms, filename):
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
        srDir= dirString  + "/SearchResults/" +"result"+ filename.replace(".pdf", "") + "searchResult.pdf"
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
    for line in searchTerms:
        for field in line:
            title += field.text() + " "
    print(summarize(text=text, word_count=400))





#GUI
class External(QThread):
    """
    Runs the scanning thread.
    """



    countChanged = pyqtSignal(int)
    directory = ""
    dirString = ""
    searchTerms = []
    currentBookNr = 0

    def run(self):
        self.ThreadRunContent()

    def ThreadRunContent(self):
        for file in os.listdir(self.directory):
            self.currentBookNr += 1
            print(self.currentBookNr)
            self.ReadWrapper(self.dirString,file, self.currentBookNr, self.searchTerms)
            self.countChanged.emit(self.currentBookNr)

    def ReadWrapper(self, dirString, file, currentBookNr, searchTerms):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"):
            Read(dirString + "/" + filename, currentBookNr, searchTerms,
                 dirString=dirString, filename=filename)

class vector2():
    x=0
    y=0


class Window(QMainWindow):
    dirString = "/Users/"
    directory = os.fsencode(dirString)
    searchTermsLines = []
    renderedPDFS = []
    pdfLayer1DocLimit = 4
    pdfLayer2DocLimit = 4
    currentDocsPDFLayer1 =0
    currentDocsPDFLayer2 = 0

    searchTermBoxes = []

    PDFImageHoldersInGrid = []



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
        self.InstiantiateProfileButton(buttonsContainer)
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

        #PDF renderers
        self.PDFRenderGrid = QGridLayout()
        uiContainer.addLayout(self.PDFRenderGrid)
        self.FillGrid()

        #Add layers to super container

        layout.addLayout(uiContainer)
        #self.setLayout(mainWidget)

        self.show()

    def GetPictureFromThread(self):
        pass


    def Profile(self):
        import cProfile
        cProfile.runctx('self.ReadForProfiler()', globals(), locals())

    def ReadForProfiler(self):
        tempSearchTerms = []
        for searchLine in self.searchTermBoxes:
            tempSearchTerms.append(searchLine.searchfields)
        for file in os.listdir(self.directory):
            filename = os.fsdecode(file)
            if filename.endswith(".pdf"):
                Read(self.dirString + "/" + filename, 0, tempSearchTerms,
                     dirString=self.dirString, filename=filename)

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

    def InstiantiateProfileButton(self, vbox):
        self.desc = QPushButton("Profile")
        self.desc.clicked.connect(self.Profile)
        vbox.addWidget(self.desc)

    def InstantiateSearchButton(self, vbox):
        self.startSearchButton = QPushButton("Search")
        self.startSearchButton.move(100, 70)
        self.startSearchButton.clicked.connect(self.RunProgram)
        vbox.addWidget(self.startSearchButton)

    def InstantiateScrollArea(self, x, y):
        #Prapre container to add images to and scroll area
        #Layout
        scrollArea = QScrollArea(widgetResizable=True)
        content_widget = QWidget()
        scrollArea.setWidget(content_widget)
        imagesHolder = QVBoxLayout(content_widget)
        self.PDFRenderGrid.addWidget(scrollArea, x, y)

        #Data
        container = RenderPDFContainer()
        container.x=x
        container.y=y
        container.scrollAreaImagesHolder = imagesHolder
        container.id = x + y
        self.PDFImageHoldersInGrid.append(container)
        return scrollArea


    def AddImageToRender(self, pdfPath, pixmap):
        '''Called from the thread. Adding an image to the render.'''
        # Actual images
        imageLabel = QLabel(self)
        imageLabel.setPixmap(pixmap)


        #so which image holder will it be? The one containing our PDF
        selectedRenderer = None
        for renderPDFContainer in self.PDFImageHoldersInGrid:
            if renderPDFContainer.pdf is pdfPath:
                selectedRenderer = renderPDFContainer

        #If the PDF has not started rendering yet so doesnt have a spot
        if selectedRenderer is None:
            for renderPDFContainer in self.PDFImageHoldersInGrid:
                if renderPDFContainer.pdf is "":
                    selectedRenderer = renderPDFContainer
                    renderPDFContainer.pdf = pdfPath

        selectedRenderer.scrollAreaImagesHolder.addWidget(imageLabel)
        imageLabel.height = pixmap.height()

    def FillGrid(self):
        for i in range(0, AppSettings.SettingsMenu.documentShowRows):
            for o in range(0, AppSettings.SettingsMenu.documentShowColumns):
                self.InstantiateScrollArea(i,o)

    def RenderPDFsIfAvailable(self):
        # '''Checks if there are search result PDFs. If there are and they are not yet rendering adds a request to the threaded rendering. '''
        # # make directory and write to it
        # if not os.path.exists(self.dirString + "/SearchResults/"):
        #     os.makedirs(self.dirString + "/SearchResults/")
        #
        # #Loop through search results directory
        # dirName =self.dirString + "/SearchResults/"
        # searchResultsDir = os.listdir(dirName)
        # pathNU, dirsNU, files = next(os.walk(dirName))
        # print(len(files))
        #
        # #Import the threaded renderer
        # import SearchPDF as spdf
        # self.threadRenderer = spdf.DocForm()
        #
        #
        # if len(files) is not 0:
        #     for searchResult in searchResultsDir:
        #         pdfPath = os.fsdecode(dirName + str(searchResult))
        #         print("Path for new generated PDF:" + str(pdfPath))
        #         if not self.renderedPDFS.__contains__(pdfPath) and pdfPath.__contains__(".pdf"):
        #             self.threadRenderer.startDocRender(pdfPath)
        pass




    def getFolderPath(self):

        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.dirString = str(folder)
        print(self.dirString)
        self.directory = os.fsencode(self.dirString)

    def RunProgram(self):
        for searchLine in self.searchTermBoxes:
            self.searchTermsLines.append(searchLine.searchfields)
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
        self.PDFSearchTask.searchTerms = self.searchTermsLines
        self.PDFSearchTask.currentBookNr = saveCount

        #Connect multithreaded counter
        self.PDFSearchTask.countChanged.connect(self.onCountChanged)
        self.PDFSearchTask.start()

    def onCountChanged(self, value):
        self.progbar.setValue(value)
        self.RenderPDFsIfAvailable()



def StartApp():
    App = QApplication(sys.argv)
    window = Window()
    from Menubar import ShowMenuItems
    menu = ShowMenuItems(mainWindow=window)
    # menu.__init__()
    sys.exit(App.exec())

StartApp()


