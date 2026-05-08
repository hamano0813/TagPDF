import sys

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QFile, QIODeviceBase

from ui.main_window import MainWindow
from res import *

if __name__ == "__main__":
    QtCore.QLoggingCategory.setFilterRules("qt.pdf.links.warning=false")
    app = QtWidgets.QApplication(sys.argv)
    app.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Light)  # type: ignore[attr-defined]
    app.setStyle("Fusion")
    qss = QFile(":/style.qss")
    qss.open(QIODeviceBase.OpenModeFlag.ReadOnly)
    stylesheet = qss.readAll().toStdString()
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(":/icon.png"))
    window.show()
    sys.exit(app.exec())
