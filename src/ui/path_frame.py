import os

from PySide6 import QtWidgets, QtCore, QtGui
from sqlalchemy.orm.session import sessionmaker

from core import functions


class PathModel(QtCore.QAbstractTableModel):
    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self._session = session_maker()
        self._paths: list[str] = list()
        self._columns = {'文件名': "name", '标题': "tit", "文号": "num"}
        self._data: list[list[str]] = list()

    def set_paths(self, paths: list[str]) -> None:
        self._paths = paths
        self.refresh()

    def refresh(self):
        self._data = list()
        for path in self._paths:
            if pdf := functions.get_pdf_by_path(self._session, path):
                self._data.append([getattr(pdf, v) for v in self._columns.values()])
            else:
                self._data.append([os.path.basename(path), "", ""])
        self.layoutChanged.emit()

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole = ...) -> any:
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return list(self._columns.keys())[section]

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._paths)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._columns)

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole = ...) -> any:
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if self._data[index.row()][1]:
                return QtGui.QBrush(QtCore.Qt.GlobalColor.cyan)
        return None


class PathFrame(QtWidgets.QFrame):
    selectChanged = QtCore.Signal(str)

    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self.setObjectName("PathFrame")
        self._model = PathModel(session_maker=session_maker)

        self._table = QtWidgets.QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.verticalHeader().hide()
        self._table.setColumnWidth(0, 280)
        self._table.setColumnWidth(1, 320)
        self._table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._table)

        self._table.clicked.connect(lambda index: self.selectChanged.emit(self.paths[index.row()]))
        self.refresh = self._model.refresh

    @property
    def paths(self):
        return self._model._paths

    def set_paths(self, paths: list[str]):
        self._model.set_paths(paths)
        self.selectChanged.emit("")
