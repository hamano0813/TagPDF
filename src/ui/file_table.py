from PySide6.QtCore import Qt, QAbstractTableModel, Signal
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PySide6.QtGui import QBrush
from sqlalchemy.orm.session import sessionmaker

from core.model import PDF


class FileModel(QAbstractTableModel):
    def __init__(self, parent=None, session_maker: sessionmaker = None):
        super().__init__(parent)
        self._paths = []
        self._titles = []
        self._columns = ['文件路径', '标题']
        self._session = session_maker()

    def headerData(self, section, orientation, role=...):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._columns[section]

    def rowCount(self, parent=...):
        return len(self._paths)

    def columnCount(self, parent=...):
        return 2

    def data(self, index, role=...):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return self._paths[index.row()]
            return self._titles[index.row()]
        if role == Qt.ItemDataRole.BackgroundRole:
            if self._titles[index.row()]:
                return QBrush(Qt.cyan)
        return None

    def set_files(self, files):
        self._paths = files
        self.refresh_titles()

    def refresh_titles(self):
        self._titles = []
        for file in self._paths:
            if pdf := self._session.query(PDF).filter_by(fp=file).all():
                self._titles.append(pdf[0].tit)
            else:
                self._titles.append('')
        self.layoutChanged.emit()


class FileTable(QTableView):
    selectChanged = Signal(str)

    def __init__(self, parent=None, session_maker: sessionmaker = None):
        super().__init__(parent)
        self._model = FileModel(session_maker=session_maker)
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()
        self.setColumnWidth(0, 600)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.clicked.connect(self.select_path)

    def set_files(self, files):
        self._model.set_files(files)

    def refresh(self):
        self._model.refresh_titles()

    def select_path(self):
        index = self.currentIndex()
        if not index.isValid():
            return
        self.selectChanged.emit(self._model._paths[index.row()])
