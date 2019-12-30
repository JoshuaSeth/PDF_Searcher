from PyQt5.QtWidgets import QPushButton, QLineEdit, QColorDialog

class ColorPicker(QPushButton):
    def __init__(self, text):
        super().__init__(text)

    currentColor = None

class LineEditColor(QLineEdit):
    colorPicker = None

    def __init__(self, text):
        super().__init__(text)
        self.AddColorPicker()

    def AddColorPicker(self):
        # First add color picker
        self.colorPicker = ColorPicker("")
        self.colorPicker.setFixedWidth(20)
        self.colorPicker.setFixedHeight(20)
        self.colorPicker.setStyleSheet("background-color: yellow")
        self.colorPicker.clicked.connect(lambda: self.SetColorPickerColor(self.colorPicker))

    def SetColorPickerColor(self, picker):
        picker.currentColor = QColorDialog.getColor()
        picker.setStyleSheet("background-color: " + picker.currentColor.name())

