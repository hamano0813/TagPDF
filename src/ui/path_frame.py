import os

from PySide6 import QtWidgets, QtCore, QtGui
from sqlalchemy.orm.session import sessionmaker

from core import functions


class PathModel(QtCore.QAbstractTableModel):
    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self._paths: list[str] = list()
        self._columns = {'文件名': "name", '标题': "tit", "文号": "num"}
        self._session = session_maker()

    def info(self, r_idx: int):
        path = self._paths[r_idx]
        if pdf := functions.get_pdf_by_path(self._session, path):
            return [getattr(pdf, v) for v in self._columns.values()]
        return [os.path.basename(path), "", ""]

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole = ...) -> any:
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return list(self._columns.keys())[section]

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._paths)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._columns)

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole = ...) -> any:
        info = self.info(index.row())
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return info[index.column()]
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if info[1]:
                return QtGui.QBrush(QtCore.Qt.GlobalColor.cyan)
        return None


class PathFrame(QtWidgets.QFrame):
    selectChanged = QtCore.Signal(str)

    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self.setObjectName("PathFrame")
        self._model = PathModel(session_maker=session_maker)
        # self._proxy = QtCore.QSortFilterProxyModel()
        # self._proxy.setSourceModel(self._model)

        self._table = QtWidgets.QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.verticalHeader().hide()
        self._table.setColumnWidth(0, 300)
        self._table.setColumnWidth(1, 300)
        self._table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._table)

        self._table.clicked.connect(self.change_select)
        self.paths = self._model._paths
        self.layoutChanged = self._model.layoutChanged

    def set_paths(self, paths: list[str]):
        self._model._paths = paths
        self._model.layoutChanged.emit()
        self.selectChanged.emit("")

    def change_select(self, index: QtCore.QModelIndex):
        # idx = self._proxy.mapToSource(index)
        self.selectChanged.emit(self._model._paths[index.row()])
