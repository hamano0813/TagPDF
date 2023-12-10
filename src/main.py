import sys

from PySide6 import QtWidgets

from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    stylesheet = open('../res/style.qss', 'r', encoding='utf-8').read()
    print(stylesheet)
    app.setStyleSheet(stylesheet)
    sys.exit(app.exec())
