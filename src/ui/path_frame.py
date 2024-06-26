import os

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QMouseEvent
from sqlalchemy.orm.session import sessionmaker

from core import functions


class PathModel(QtCore.QAbstractTableModel):
    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self._session = session_maker()
        self._paths: list[str] = list()
        self._columns = {"文件名": "name", "标题": "tit", "文号": "num"}
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
            if orientation == QtCore.Qt.Orientation.Vertical:
                return f"{section+1} "

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


class PathFrame(QtWidgets.QTableView):
    selectChanged = QtCore.Signal(str)

    def __init__(self, session_maker: sessionmaker = None):
        super().__init__(parent=None)
        self.setObjectName("PathFrame")
        self._model = PathModel(session_maker=session_maker)

        self.setModel(self._model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setFixedWidth(40)
        self.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setColumnWidth(0, 280)
        self.setColumnWidth(1, 320)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.clicked.connect(lambda index: self.selectChanged.emit(self._model._paths[index.row()]))
        self.refresh = self._model.refresh

    def set_paths(self, paths: list[str]):
        self._model.set_paths(paths)
        self.selectChanged.emit("")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # 判断mouse点击的位置是否在表格内，如果不在，则清空选择
        if not self.indexAt(event.pos()).isValid():
            self.setCurrentIndex(QtCore.QModelIndex())
            self.selectChanged.emit("")
        return super().mousePressEvent(event)