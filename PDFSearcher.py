#Program
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
import PyPDF2
import re
import fitz

from fitz.utils import getColor  # function delivers RGB triple for a color name

from SearchBox import SearchBox

#GUI
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QScrollArea, QWidget, QVBoxLayout, QProgressBar, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QApplication, QCheckBox, QGridLayout, QGroupBox, QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QDockWidget, QTabBar
import sys

import ctypes.util
print(ctypes.util.find_library("leptonica"))
import ocrmypdf

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
        try:
            Text = PageObj.extractText()
        except:
            print("exception in text extraction")


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
    SavePDFPagesAsFile(fileString, savedPages, saveCount, dirString, searchTermsLines, filename, test=False)


def SavePDFPagesAsFile(fileString, pages, saveCount, dirString, searchTerms, filename, test):
    if len(pages) is not 0:
        inputpdfFitz = fitz.open(fileString)
        fitzOutput = fitz.open()
        donePages = []



        sawSearchTerms = False

        # save pages with search results to a new pdf
        sawSearchTerms = MakeSearchResultDoc(donePages, sawSearchTerms, fitzOutput, inputpdfFitz, pages,
                                               searchTerms)

        # If search doenst return results it needs marking with OCR
        # if sawSearchTerms is False or test:
        #     fitzOutput = OCRDoc(donePages, fileString, fitzOutput, pages, sawSearchTerms, searchTerms, yellow)

        #make directory and write to it
        if not os.path.exists(dirString  + "/SearchResults/"):
            os.makedirs(dirString  + "/SearchResults/")

        ocrstring = ""
        # if not sawSearchTerms:
        #     ocrstring="OCRed"
        srDirFitz = dirString  + "/SearchResults/" +"result"+ filename.replace(".pdf", "") + ocrstring + "FITZsearchResult.pdf"

        print(type(fitzOutput))
        print(fitzOutput.pageCount)
        if fitzOutput.pageCount>0:
            fitzOutput.save(srDirFitz)

        # PrintSummaryOfResults(srDir=srDirFitz, searchTerms=searchTerms)


def OCRDoc(donePages, fileString, fitzOutput, pages, sawSearchTerms, searchTerms, yellow):
    print("OCriNG!!!!!!")
    ocrfilestring = fileString.replace(".pdf", "") + "OCRed.pdf"
    ocrmypdf.ocr(fileString, ocrfilestring, deskew=True, force_ocr=True)
    inputpdfFitz = fitz.open(ocrfilestring)
    fitzOutput = fitz.open()
    MakeSearchResultDoc(donePages, sawSearchTerms, fitzOutput, inputpdfFitz, pages,
                        searchTerms)
    return fitzOutput


def MakeSearchResultDoc(donePages, findsSearchTerms, fitzOutput, inputpdfFitz, pages, searchTerms):
    for page in pages:
        for plusandminus in range(-2, 2):
            if not donePages.__contains__(
                    page + plusandminus) and page + plusandminus > 0 and page + plusandminus < inputpdfFitz.pageCount:
                donePages.append(page + plusandminus)

                # Fitz procedure
                pageToAddFitz = inputpdfFitz.loadPage(page + plusandminus)
                for line in searchTerms:
                    for word in line:
                        rl = pageToAddFitz.searchFor(word.text())
                        # If search returns results which means its text and no OCR is needed
                        if len(rl) > 0:
                            findsSearchTerms = True
                        for r in rl:
                            hitTermColor = word.colorPicker.currentColor.getRgbF()
                            convertHTT = (hitTermColor[0], hitTermColor[1], hitTermColor[2])
                            pageToAddFitz.drawRect(r, color=convertHTT, fill=convertHTT, overlay=False)

                fitzOutput.insertPDF(docsrc=inputpdfFitz, from_page=page + plusandminus, to_page=page + plusandminus)
    return findsSearchTerms



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
    renderedPDFS = []
    pdfLayer1DocLimit = 4
    pdfLayer2DocLimit = 4
    currentDocsPDFLayer1 =0
    currentDocsPDFLayer2 = 0

    searchLinesOfBoxes = []

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
        #self.AddDockTest(buttonsContainer)
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
        for searchLine in self.searchLinesOfBoxes:
            tempSearchTerms.append(searchLine.searchfields)
        for file in os.listdir(self.directory):
            filename = os.fsdecode(file)
            if filename.endswith(".pdf"):
                Read(self.dirString + "/" + filename, 0, tempSearchTerms,
                     dirString=self.dirString, filename=filename)

    def AddSearchBox(self, title):
        sb = SearchBox()
        sb.program = self
        #This is necessary because other wise all class instances of searchbox refer to the same searchterms array
        sb.searchFields = []
        sb.AddSearchField()
        self.SearchTermsGrid.addWidget(sb.Get(title))
        self.searchLinesOfBoxes.append(sb.searchFields)


    # def AddDockTest(self, vbox):
    #     self._tabOptions = QTabWidget(self)
    #     self._tabOptions.setLayoutDirection(Qt.LeftToRight)
    #     self._tabOptions.setDocumentMode(False)
    #     self._tabOptions.setTabsClosable(False)
    #     self._tabOptions.setMovable(False)
    #
    #     self.dock = QDockWidget('Tab Options', self)
    #     self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
    #     self.dock.setWidget(self._tabOptions)
    #     vbox.addWidget(self.progbar)


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
        #Test
        pages = []
        for i in range(0,1000):
            pages.append(i)
        SavePDFPagesAsFile("test.pdf", pages, 333, self.dirString, self.searchLinesOfBoxes, "Test.pdf", test=True)


        for searchLine in self.searchLinesOfBoxes:
            print(searchLine)
            print("Terms:")
            for lineedit in searchLine:
                print(lineedit.text())
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
        self.PDFSearchTask.searchTerms = self.searchLinesOfBoxes
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


