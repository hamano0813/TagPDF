import os

from PySide6 import QtWidgets, QtCore, QtGui

from core import functions


class CheckFlowLayout(QtWidgets.QLayout):
    widthChanged = QtCore.Signal(int)

    def __init__(self):
        super().__init__(parent=None)
        self.setObjectName("CheckFlowLayout")
        self._item_list: list[QtWidgets.QLayoutItem] = []

    def __del__(self) -> None:
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QtWidgets.QLayoutItem) -> None:
        self._item_list.append(item)

    def removeItem(self, item: QtWidgets.QLayoutItem) -> None:
        self._item_list.remove(item)

    def count(self) -> int:
        return len(self._item_list)

    def itemAt(self, index: int) -> QtWidgets.QLayoutItem | None:
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index) -> QtWidgets.QLayoutItem | None:
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self) -> QtCore.Qt.Orientations:
        return QtCore.Qt.Orientation.Horizontal

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QtCore.QRect) -> None:
        super(CheckFlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:
        size = QtCore.QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(self.contentsMargins().top() * 2, self.contentsMargins().left() * 2)
        return size

    def _do_layout(self, rect: QtCore.QRect, test_only: bool) -> int:
        line_height = 0
        spacing = self.spacing()
        x = rect.x() + spacing
        y = rect.y() + spacing
        for item in self._item_list:
            style: QtWidgets.QStyle = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Orientation.Horizontal,
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Orientation.Vertical,
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x > rect.right() and line_height > 0:
                x = rect.x() + spacing
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        if self.count():
            self.widthChanged.emit(max(i.widget().width() for i in self._item_list) + spacing * 2)
        return y + line_height - rect.y()


class CheckGroup(QtWidgets.QGroupBox):
    checkChanged = QtCore.Signal()

    def __init__(self, title: str):
        super().__init__(title, parent=None)
        self.setObjectName("CheckGroup")
        self.setTitle(title)
        
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        self.container_widget = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.container_widget)
        
        self.container_layout = CheckFlowLayout()
        self.container_layout.setSpacing(8)
        self.container_widget.setLayout(self.container_layout)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
        
        self.container_layout.widthChanged.connect(self.setMinimumWidth)
        self._checks: list[QtWidgets.QCheckBox] = list()

    @property
    def selected(self) -> list[str]:
        return [check.text() for check in self._checks if check.isChecked()]

    def checks(self) -> list[str]:
        return [check.text() for check in self._checks]

    def set_checks(self, checks: list[str]):
        self.clear()
        for check in checks:
            self.add_check(check)

    def add_check(self, check_text: str):
        check = QtWidgets.QCheckBox(check_text)
        check.setObjectName("#CheckBox")
        check.clicked.connect(self.checkChanged.emit)
        self._checks.append(check)
        self.container_layout.addWidget(check)

    def clear(self):
        while self._checks:
            check = self._checks.pop()
            check.clicked.disconnect()
            self.container_layout.removeWidget(check)
            check.deleteLater()


class FilterFrame(QtWidgets.QFrame):
    filterChanged = QtCore.Signal(list)

    def __init__(self, session_maker):
        super().__init__(parent=None)
        self._session = session_maker()

        self._pub = CheckGroup("发布")
        self._rls = CheckGroup("年份")
        self._tag = CheckGroup("标签")
        self._btn = QtWidgets.QPushButton("导出当前列表")
        self._btn.setObjectName("PushButton")

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 3)
        self.layout().addWidget(self._pub)
        self.layout().addWidget(self._rls)
        self.layout().addWidget(self._tag)
        self.layout().addWidget(self._btn)

        self._pub.checkChanged.connect(self.check_changed)
        self._rls.checkChanged.connect(self.check_changed)
        self._tag.checkChanged.connect(self.check_changed)

    def check_changed(self):
        pub = self._pub.selected
        rls = list(map(int, self._rls.selected))
        tag = self._tag.selected
        pdfs = functions.get_pdf_by_filters(self._session, pub, rls, tag)
        paths = []
        for pdf in pdfs:
            if os.path.exists(pdf.fp):
                paths.append(pdf.fp)
            else:
                functions.delete_pdf(self._session, pdf)
        self.filterChanged.emit(paths)

    def refresh(self):
        self._pub.set_checks(functions.get_all_pub(self._session))
        self._rls.set_checks(list(map(str, functions.get_all_rls(self._session))))
        self._tag.set_checks(functions.get_all_tag(self._session))

    def clear(self):
        self._pub.clear()
        self._rls.clear()
        self._tag.clear()
