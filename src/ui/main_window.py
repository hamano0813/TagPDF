import os
import time
import zipfile

from PySide6 import QtWidgets, QtCore

from PySide6.QtWidgets import QSplitter, QTabWidget, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ui import ScanFrame, PdfFilter, FileTable, PreviewFrame, InfoFrame
from core.model import Base, TAG


class MainWindow(QtWidgets.QSplitter):
    def __init__(self):
        super().__init__()
        engine = create_engine('sqlite:///pdf.db3', echo=False)
        Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(bind=engine)

        self.setWindowTitle('TagPDF v1.0')
        self.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(1440, 720)

        scan_frame = ScanFrame(root='/')
        filter_frame = PdfFilter(session_maker=self.sessionmaker)
        file_table = FileTable(session_maker=self.sessionmaker)
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

        self.addWidget(left_frame)
        self.addWidget(file_table)
        self.addWidget(right_frame)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 5)
        self.setStretchFactor(2, 2)

        scan_frame.folderChanged.connect(file_table.set_files)
        file_table.selectChanged.connect(preview_frame.document().load)
        file_table.selectChanged.connect(info_frame.set_path)
        info_frame.infoChanged.connect(file_table._model.refresh_titles)
        info_frame.infoChanged.connect(lambda: filter_frame.refresh(True))
        filter_frame.filterChanged.connect(file_table.set_files)

        scan_frame._btn.clicked.connect(filter_frame.clear)
        filter_frame.export_btn.clicked.connect(self.export)

        filter_frame.refresh()
        filter_frame.check_changed()

        self.model = file_table._model

    def export(self):
        pdfs = self.model._paths
        if not pdfs:
            return
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, '选择导出路径', f'C:/Users/{os.getlogin()}/Desktop')
        if not path:
            return
        path += f"/{time.strftime('PDF_%Y%m%d%H%M%S', time.localtime())}.zip"

        zip_file = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        for pdf in pdfs:
            zip_file.write(pdf, os.path.basename(pdf))
        zip_file.close()

    def closeEvent(self, event):
        session = self.sessionmaker()
        tags = session.query(TAG).all()
        for tag in tags:
            if not tag.pdf:
                session.delete(tag)
        session.commit()
        session.close()
        event.accept()
