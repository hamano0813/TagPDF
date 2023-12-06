import os

from PySide6.QtCore import Qt, QDir, QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QFrame, QPushButton, QTreeView, QFileSystemModel, QVBoxLayout


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.hidden_dirs = [
            'c:/windows',
            'c:/program files',
            'c:/program files (x86)',
            'c:/programdata',
            'c:/users/all users',
        ]

    def filterAcceptsRow(self, row, parent):
        index = self.sourceModel().index(row, 0, parent)
        path = self.sourceModel().filePath(index)
        if path.lower() in self.hidden_dirs:
            return False
        return super().filterAcceptsRow(row, parent)


class DirModel(QFileSystemModel):
    def __init__(self, root):
        super().__init__()
        self.setRootPath(root)
        self.setReadOnly(True)
        self.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)

    def columnCount(self, parent=...):
        return 1


class TreeView(QTreeView):
    rootChanged = Signal(str)
    selectChanged = Signal(list)

    def __init__(self, parent=None, root: str = '/'):
        super().__init__(parent)
        self.header().hide()
        self.proxy = FilterProxyModel()
        self.proxy.setSourceModel(DirModel(root=root))
        self.proxy.sort(0, Qt.AscendingOrder)
        self.setModel(self.proxy)
        self.expandToDepth(1)
        self.expand(self.proxy.mapFromSource(self.proxy.sourceModel().index(root)))

    def scan_dir(self):
        index = self.proxy.mapToSource(self.currentIndex())
        path = self.proxy.sourceModel().filePath(index)
        disk_path = [chr(i) + ':/' for i in range(ord('A'), ord('Z') + 1)]
        disk_path.append('/')
        if path.upper() in disk_path:
            return False
        pdf_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_list.append(os.path.join(root, file).replace('\\', '/'))
        self.rootChanged.emit(path)
        self.selectChanged.emit(pdf_list)
        return True

    def set_root(self, root: str):
        self.proxy.sourceModel().setRootPath(root)


class DirTree(QFrame):
    def __init__(self, parent=None, root: str = '/'):
        super().__init__(parent)
        self.tree_view = TreeView(root=root)
        self.scan_btn = QPushButton(self.tr('Scan PDF'))
        self.scan_btn.clicked.connect(self.tree_view.scan_dir)
        self.rootChanged = self.tree_view.rootChanged
        self.selectChanged = self.tree_view.selectChanged

        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        layout.addWidget(self.scan_btn)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)
