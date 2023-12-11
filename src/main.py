import sys

from PySide6 import QtWidgets

from ui.main_window import MainWindow
from res import *

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    qss_file = QtCore.QFile(":/style.qss")
    qss_file.open(QtCore.QFile.ReadOnly)
    stylesheet = qss_file.readAll().data().decode()
    app.setStyleSheet(stylesheet)
    sys.exit(app.exec())
