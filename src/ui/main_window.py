import os
import time
import zipfile

from PySide6.QtWidgets import QSplitter, QTabWidget, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .scan_frame import ScanFrame
from .pdf_filter import PdfFilter
from .file_table import FileTable
from .preview_frame import PreviewFrame
from .info_editor import InfoEditor
from core.model import Base, TAG
from res import *


class MainWindow(QSplitter):
    def __init__(self):
        super().__init__()
        engine = create_engine('sqlite:///pdf.db3', echo=False)
        Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(bind=engine)

        self.setWindowTitle('TagPDF v1.0')
        self.setWindowIcon(QIcon(":/icon.png"))
        self.setOrientation(Qt.Horizontal)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(1440, 720)

        self.scan_frame = ScanFrame(root='/')
        self.pdf_filter = PdfFilter(session_maker=self.sessionmaker)

        left_tab = QTabWidget()
        left_tab.addTab(self.pdf_filter, '过滤查询')
        left_tab.addTab(self.scan_frame, '扫描添加')
        self.addWidget(left_tab)

        self.file_table = FileTable(session_maker=self.sessionmaker)
        self.addWidget(self.file_table)

        self.right_splitter = QSplitter()
        self.right_splitter.setOrientation(Qt.Vertical)
        self.right_splitter.setHandleWidth(1)

        self.preview_frame = PreviewFrame()
        self.info_editor = InfoEditor(session_maker=self.sessionmaker)

        self.right_splitter.addWidget(self.preview_frame)
        self.right_splitter.addWidget(self.info_editor)
        self.addWidget(self.right_splitter)

        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 5)
        self.setStretchFactor(2, 2)

        self.scan_frame.folderChanged.connect(self.file_table.set_files)
        self.file_table.selectChanged.connect(self.preview_frame.document().load)
        self.file_table.selectChanged.connect(self.info_editor.set_path)
        self.info_editor.infoChanged.connect(self.file_table._model.refresh_titles)
        self.info_editor.infoChanged.connect(lambda :self.pdf_filter.refresh(True))
        self.pdf_filter.filterChanged.connect(self.file_table.set_files)

        self.scan_frame._btn.clicked.connect(self.pdf_filter.clear)
        self.pdf_filter.export_btn.clicked.connect(self.export)

        self.pdf_filter.refresh()
        self.pdf_filter.check_changed()

    def export(self):
        pdfs = self.file_table._model.files
        if not pdfs:
            return
        path = QFileDialog.getExistingDirectory(self, '选择导出路径', f'C:/Users/{os.getlogin()}/Desktop')
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
