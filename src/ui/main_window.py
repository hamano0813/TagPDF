from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .dir_tree import DirTree
from .file_table import FileTable
from .pdf_view import PdfView
from .info_editor import InfoEditor
from core.model import Base, TAG


class MainWindow(QSplitter):
    def __init__(self):
        super().__init__()
        engine = create_engine('sqlite:///pdf.db3', echo=False)
        Base.metadata.create_all(engine)
        self.sessionmaker = sessionmaker(bind=engine)

        self.setWindowTitle('TagPDF v0.5')
        self.setOrientation(Qt.Horizontal)
        self.setHandleWidth(1)
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(1280, 720)

        self.dir_tree = DirTree(root='C:/')
        self.addWidget(self.dir_tree)

        self.file_table = FileTable(session_maker=self.sessionmaker)
        self.addWidget(self.file_table)

        self.right_splitter = QSplitter()
        self.right_splitter.setOrientation(Qt.Vertical)
        self.right_splitter.setHandleWidth(1)

        self.pdf_view = PdfView()
        self.info_editor = InfoEditor(session_maker=self.sessionmaker)

        self.right_splitter.addWidget(self.pdf_view)
        self.right_splitter.addWidget(self.info_editor)
        self.addWidget(self.right_splitter)

        # 调整splitter
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 5)
        self.setStretchFactor(2, 2)

        self.dir_tree.selectChanged.connect(self.file_table.set_files)
        self.file_table.selectChanged.connect(self.pdf_view.document().load)
        self.file_table.selectChanged.connect(self.info_editor.set_path)
        self.info_editor.infoChanged.connect(self.file_table.model.refresh_titles)

    def closeEvent(self, event):
        session = self.sessionmaker()
        tags = session.query(TAG).all()
        for tag in tags:
            if not tag.pdf:
                session.delete(tag)
        session.commit()
        session.close()
        event.accept()
