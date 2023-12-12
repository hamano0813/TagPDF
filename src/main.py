import sys

from PySide6 import QtWidgets, QtGui

from ui.main_window import MainWindow
from res import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qss = QtCore.QFile(":/style.qss")
    qss.open(QtCore.QFile.ReadOnly)
    stylesheet = qss.readAll().data().decode()
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(":/icon.png"))
    window.show()
    sys.exit(app.exec())
