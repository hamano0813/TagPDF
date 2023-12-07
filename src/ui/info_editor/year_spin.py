from PySide6.QtWidgets import QSpinBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator


class YearSpin(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignRight)
        self.setRange(1950, 2050)
        self.setWrapping(True)
        self.lineEdit().setValidator(QRegularExpressionValidator(r'^\d{0,4}$'))
        self.setStyleSheet("""
            QSpinBox { 
            padding-left: 5px; 
            padding-right: 5px; 
            border-width:1px; 
            border-style: solid; 
            border-color:gray; }
            """)

    def textFromValue(self, val):
        if val == 1950:
            return ''
        return super().textFromValue(val) + ' 年'

    def valueFromText(self, text):
        if text == '':
            return 1950
        return super().valueFromText(text.rstrip(' 年'))

    def value(self):
        if self.text() == '':
            return None
        return super().value()

    def setValue(self, val):
        if val is None:
            self.clear()
        else:
            super().setValue(val)

    def clear(self):
        self.setValue(1950)

    def setEnabled(self, enable):
        self.lineEdit().setReadOnly(not enable)
        self.setRange(1950, 1950 if not enable else 2050)
