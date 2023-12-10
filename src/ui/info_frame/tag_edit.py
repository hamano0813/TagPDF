from PySide6 import QtWidgets, QtCore, QtGui


class InputFlowLayout(QtWidgets.QLayout):
    heightChanged = QtCore.Signal(int)
    widthChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InputFlowLayout")
        self.setSpacing(3)
        self._item_list = []

    def __del__(self) -> None:
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item) -> None:
        self._item_list.insert(-1, item)

    def removeItem(self, item):
        self._item_list.remove(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(InputFlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(self.contentsMargins().top() * 2, self.contentsMargins().top() * 2)
        return size

    def _do_layout(self, rect: QtCore.QRect, test_only: bool):
        line_height = 0
        spacing = self.spacing()
        x = rect.x() + spacing
        y = rect.y() + spacing
        for item in self._item_list:
            style: QtWidgets.QStyle = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtWidgets.QSizePolicy.ControlType.PushButton,
                QtCore.Qt.Orientation.Vertical
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
                item.setGeometry(item_rect := QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
                if isinstance(item.widget(), QtWidgets.QLineEdit):
                    self.heightChanged.emit(item_rect.bottom() + spacing + 1)
                    item_rect.setRight(rect.right() - space_x)
                    item.setGeometry(item_rect)
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        if self.count() > 1:
            self.widthChanged.emit(max(i.widget().width() for i in self._item_list[:-1]) + spacing * 2)
        return y + line_height - rect.y()


class TagLabel(QtWidgets.QFrame):
    def __init__(self, tag: str):
        super().__init__(parent=None)
        self.setObjectName("TagLabel")
        self.setProperty("hover", "false")

        self.tag_text = QtWidgets.QLabel(tag)
        self.tag_text.setObjectName("TagText")
        self.tag_text.setWordWrap(False)
        self.tag_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.tag_btn = QtWidgets.QPushButton("×")
        self.tag_btn.setObjectName("TagButton")

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.tag_text)
        self.layout().addWidget(self.tag_btn)

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        self.setProperty("hover", "true")
        self.setStyle(self.style())
        return super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self.setProperty("hover", "false")
        self.setStyle(self.style())
        return super().leaveEvent(event)

    def sizeHint(self):
        return QtCore.QSize(30, 25)


class TagEdit(QtWidgets.QFrame):
    tagChanged = QtCore.Signal(list)

    def __init__(self):
        super().__init__(parent=None)
        self._tags: dict[str, TagLabel] = dict()

        self._box = QtWidgets.QTextEdit(self)
        self._box.setContentsMargins(0, 0, 0, 0)
        self._box.setReadOnly(True)
        self._box.setFixedHeight(self.sizeHint().height())

        self._line = QtWidgets.QLineEdit()
        self._line.setObjectName("TagLine")
        self._line.sizeHint = lambda: QtCore.QSize(50, 25)

        self.setLayout(InputFlowLayout())
        self.layout().addWidget(self._line)

        self.layout().heightChanged.connect(self.setMinimumHeight)
        self.layout().widthChanged.connect(self.setMinimumWidth)
        self._line.returnPressed.connect(self._append_tag)
        self._line.editingFinished.connect(self._append_tag)
        self.setEnabled = self._line.setEnabled

    def resizeEvent(self, event):
        self._box.setFixedSize(self.size())
        super().resizeEvent(event)

    @property
    def tags(self) -> list[str]:
        return list(self._tags.keys())

    @tags.setter
    def tags(self, tags: list[str]):
        self.clear()
        for tag in tags:
            self._add_tag(tag)

    def _append_tag(self) -> None:
        self._add_tag(self._line.text().strip())
        self._line.clear()

    def _add_tag(self, tag: str) -> None:
        if not tag or tag in self._tags:
            return
        tag_label = TagLabel(tag.strip())
        tag_label.tag_btn.clicked.connect(lambda: self._del_tag(tag))
        self._tags[tag] = tag_label
        self.layout().addWidget(tag_label)
        self.tagChanged.emit(self.tags)

    def _del_tag(self, tag: str) -> None:
        tag_label = self._tags.pop(tag)
        self.layout().removeWidget(tag_label)
        tag_label.deleteLater()
        self.tagChanged.emit(self.tags)

    def clear(self) -> None:
        for tag in self.tags:
            self._tags[tag]._delete()

    def set_completer(self, tags: list[str]):
        if not tags:
            self._line.setCompleter(QtWidgets.QCompleter())
        completer = QtWidgets.QCompleter(tags)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(5)
        completer.popup().setObjectName("TagPopup")
        self._line.setCompleter(completer)
