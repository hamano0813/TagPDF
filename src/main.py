import sys

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QFile, QIODeviceBase

from ui.main_window import MainWindow
from res import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    qss = QFile(":/style.qss")
    qss.open(QIODeviceBase.OpenModeFlag.ReadOnly)
    stylesheet = qss.readAll().toStdString()
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(":/icon.png"))
    window.show()
    sys.exit(app.exec())
