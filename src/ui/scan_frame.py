from PySide6 import QtWidgets, QtCore

from core import functions


class ProxyModel(QtCore.QSortFilterProxyModel):
    HIDDEN = (
        "c:/windows",
        "c:/program files",
        "c:/program files (x86)",
        "c:/programdata",
        "c:/users/all users",
    )

    def __init__(self):
        super().__init__()

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)
        path = self.sourceModel().filePath(index)
        if path.lower() in ProxyModel.HIDDEN:
            return False
        return super().filterAcceptsRow(source_row, source_parent)

    def lessThan(self, source_left: QtCore.QModelIndex, source_right: QtCore.QModelIndex) -> bool:
        return self.sourceModel().filePath(source_left) < self.sourceModel().filePath(source_right)


class ScanFrame(QtWidgets.QFrame):
    folderChanged = QtCore.Signal(list)

    def __init__(self, root):
        super().__init__(parent=None)
        self.setObjectName("ScanFrame")

        self._model = QtWidgets.QFileSystemModel()
        self._model.setRootPath(root)
        self._model.setReadOnly(True)
        self._model.setFilter(QtCore.QDir.Filter.AllDirs | QtCore.QDir.Filter.NoDotAndDotDot)
        self._model.columnCount = lambda *args: 1

        self._proxy = ProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.sort(0, QtCore.Qt.SortOrder.AscendingOrder)

        self._tree = QtWidgets.QTreeView()
        self._tree.setObjectName("DirTree")
        self._tree.header().hide()
        self._tree.setModel(self._proxy)
        self._tree.expandToDepth(1)
        self._tree.expand(self._proxy.mapFromSource(self._model.index(root)))

        self._btn = QtWidgets.QPushButton("扫描选中路径")
        self._btn.setObjectName("PushButton")
        self._btn.clicked.connect(self._scan)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 3)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._tree)
        self.layout().addWidget(self._btn)

    def _scan(self) -> None:
        index = self._proxy.mapToSource(self._tree.currentIndex())
        folder = self._model.filePath(index)
        paths = functions.scan_pdf(folder)
        self.folderChanged.emit(paths)
