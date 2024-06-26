import os

from PySide6 import QtWidgets, QtCore, QtGui
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import functions, model
from ui import ScanFrame, FilterFrame, PathFrame, PreviewFrame, InfoFrame


class MainWindow(QtWidgets.QSplitter):
    def __init__(self):
        super().__init__()
        engine = create_engine("sqlite:///pdf.db3", echo=False)
        model.Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(bind=engine)

        self.setWindowTitle("TagPDF v1.6")
        self.setObjectName("MainWindow")
        self.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.setHandleWidth(1)
        self.setMinimumSize(1440, 720)

        scan_frame = ScanFrame(root="/")
        self.filter_frame = FilterFrame(session_maker=self.sessionmaker)
        self.path_frame = PathFrame(session_maker=self.sessionmaker)
        preview_frame = PreviewFrame()
        info_frame = InfoFrame(session_maker=self.sessionmaker)

        left_frame = QtWidgets.QTabWidget()
        left_frame.addTab(self.filter_frame, "过滤查询")
        left_frame.addTab(scan_frame, "扫描添加")

        right_frame = QtWidgets.QSplitter()
        right_frame.setOrientation(QtCore.Qt.Orientation.Vertical)
        right_frame.setHandleWidth(1)
        right_frame.addWidget(preview_frame)
        right_frame.addWidget(info_frame)
        right_frame.setStretchFactor(0, 5)
        right_frame.setStretchFactor(1, 3)

        self.addWidget(left_frame)
        self.addWidget(self.path_frame)
        self.addWidget(right_frame)
        self.setStretchFactor(0, 3)
        self.setStretchFactor(1, 9)
        self.setStretchFactor(2, 4)

        scan_frame.folderChanged.connect(self.path_frame.set_paths)
        self.filter_frame.filterChanged.connect(self.path_frame.set_paths)
        self.path_frame.selectChanged.connect(preview_frame.set_path)
        self.path_frame.selectChanged.connect(info_frame.set_path)
        info_frame.infoChanged.connect(self.path_frame.refresh)
        info_frame.infoChanged.connect(self.filter_frame.refresh)
        scan_frame._btn.clicked.connect(self.filter_frame.refresh)
        self.filter_frame._btn.clicked.connect(self.export)

        self.filter_frame.refresh()
        self.filter_frame.check_changed()

    def export(self):
        if not (paths := self.path_frame._model._paths):
            return
        if f := QtWidgets.QFileDialog.getExistingDirectory(self, "选择导出路径", f"C:/Users/{os.getlogin()}/Desktop"):
            session = self.sessionmaker()
            functions.zip_path(paths, f, session)
            session.close()

    def closeEvent(self, event: QtCore.QEvent):
        session = self.sessionmaker()
        functions.clear_pub_if_unused(session)
        functions.clear_tag_if_unused(session)
        session.close()
        event.accept()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_F and event.modifiers() == QtCore.Qt.ControlModifier:
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle("重命名PDF")
            box.setText("是否批量重命名PDF文件？")
            box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            box.setButtonText(QtWidgets.QMessageBox.Yes, "确定")
            box.setButtonText(QtWidgets.QMessageBox.No, "放弃")
            if box.exec() == QtWidgets.QMessageBox.Yes:
                session = self.sessionmaker()
                if isinstance(result := functions.rename_pdfs(session), str):
                    QtWidgets.QMessageBox.critical(self, "错误", f"{result}\n当前被选中或正在被其他程序使用\n无法重命名")
                else:
                    self.filter_frame.check_changed()
                session.close()
        return super().keyPressEvent(event)
