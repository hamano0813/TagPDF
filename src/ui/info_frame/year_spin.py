from PySide6 import QtWidgets, QtCore, QtGui


class YearSpin(QtWidgets.QSpinBox):
    RANGE = (1980, 2030)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.setRange(*YearSpin.RANGE)
        self.setWrapping(True)
        self.lineEdit().setValidator(QtGui.QRegularExpressionValidator(r'^\d{0,4}$'))

    def textFromValue(self, val) -> str:
        if val == YearSpin.RANGE[0]:
            return ''
        return super().textFromValue(val) + ' 年'

    def valueFromText(self, text) -> int:
        if text == '':
            return YearSpin.RANGE[0]
        return super().valueFromText(text.rstrip(' 年'))

    def value(self) -> int | None:
        if self.text() == '':
            return None
        return super().value()

    def setValue(self, val) -> None:
        if val is None:
            self.clear()
        else:
            super().setValue(val)

    def clear(self) -> None:
        self.setValue(YearSpin.RANGE[0])

    def setEnabled(self, enable) -> None:
        self.lineEdit().setReadOnly(not enable)
        self.setRange(YearSpin.RANGE[0], YearSpin.RANGE[0] if not enable else YearSpin.RANGE[1])
