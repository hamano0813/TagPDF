import os

from PySide6 import QtWidgets, QtCore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core import functions, model
from ui import ScanFrame, FilterFrame, PathFrame, PreviewFrame, InfoFrame


class MainWindow(QtWidgets.QSplitter):
    def __init__(self):
        super().__init__()
        engine = create_engine('sqlite:///pdf.db3', echo=False)
        model.Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(bind=engine)

        self.setWindowTitle('TagPDF v1.0')
        self.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(1440, 720)

        scan_frame = ScanFrame(root='/')
        filter_frame = FilterFrame(session_maker=self.sessionmaker)
        path_frame = PathFrame(session_maker=self.sessionmaker)
        preview_frame = PreviewFrame()
        info_frame = InfoFrame(session_maker=self.sessionmaker)

        left_frame = QtWidgets.QTabWidget()
        left_frame.addTab(filter_frame, '过滤查询')
        left_frame.addTab(scan_frame, '扫描添加')

        right_frame = QtWidgets.QSplitter()
        right_frame.setOrientation(QtCore.Qt.Orientation.Vertical)
        right_frame.setHandleWidth(1)
        right_frame.addWidget(preview_frame)
        right_frame.addWidget(info_frame)
        right_frame.setStretchFactor(0, 5)
        right_frame.setStretchFactor(1, 3)

        self.addWidget(left_frame)
        self.addWidget(path_frame)
        self.addWidget(right_frame)
        self.setStretchFactor(0, 3)
        self.setStretchFactor(1, 9)
        self.setStretchFactor(2, 4)

        self.paths = path_frame.paths

        scan_frame.folderChanged.connect(path_frame.set_paths)
        filter_frame.filterChanged.connect(path_frame.set_paths)
        path_frame.selectChanged.connect(preview_frame.document().load)
        path_frame.selectChanged.connect(info_frame.set_path)
        info_frame.infoChanged.connect(path_frame.layoutChanged.emit)
        info_frame.infoChanged.connect(filter_frame.refresh)
        scan_frame._btn.clicked.connect(filter_frame.refresh)
        filter_frame._btn.clicked.connect(self.export)

        filter_frame.refresh()
        filter_frame.check_changed()

    def export(self):
        if not self.paths:
            return
        if not (folder := QtWidgets.QFileDialog.getExistingDirectory(
                self, '选择导出路径', f'C:/Users/{os.getlogin()}/Desktop')):
            return
        functions.zip_path(self.paths, folder)

    def closeEvent(self, event):
        session = self.sessionmaker()
        functions.clear_tag_if_unused(session)
        session.close()
        event.accept()
