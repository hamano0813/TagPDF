import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.setStyleSheet(open('../res/style.qss', 'r', encoding='utf-8').read())
    sys.exit(app.exec())
