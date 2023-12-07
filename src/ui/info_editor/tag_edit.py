from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QLineEdit, QCompleter, QLayout, QHBoxLayout, QSizePolicy


class TagLine(QLineEdit):
    def __init__(self):
        super().__init__(parent=None)
        self.setContentsMargins(7, 3, 2, 3)
        self.setStyleSheet('TagLine { border: none; }')

    def set_completer(self, tags: list[str]):
        if not tags:
            self.setCompleter(QCompleter())
        completer = QCompleter(tags)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)
        self.completer().popup().verticalScrollBar().hide()
        self.completer().popup().verticalScrollBar().setStyleSheet('QScrollBar { width: 0px; }')
        self.completer().popup().setStyleSheet('QListView { padding-left: 5px; };')
        self.completer().setMaxVisibleItems(10)

    def sizeHint(self):
        return QSize(50, 25)


class TagLabel(QFrame):
    deleteTag = Signal(str)

    def __init__(self, tag: str):
        super().__init__(parent=None)
        self.setContentsMargins(8, 0, 0, 0)
        self.setStyleSheet('TagLabel { '
                           'border: 1px solid silver; '
                           'border-radius: 4px; '
                           'background-color: gainsboro; '
                           '}')

        self._label = QLabel(tag)
        self._label.setMinimumSize(10, 10)
        self._label.setContentsMargins(0, 0, 0, 0)
        self._label.setWordWrap(False)
        self._label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self._button = QPushButton("×")
        self._button.setFixedWidth(20)
        self._button.setFlat(True)
        self._button.setStyleSheet('QPushButton:pressed { border: none; font-weight: bold; };')

        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._label)
        self.layout().addWidget(self._button)

        self._button.clicked.connect(self._delete)

    def _delete(self):
        self._label.deleteLater()
        self._button.clicked.disconnect(self._delete)
        self._button.deleteLater()
        self.deleteTag.emit(self._label.text())
        self.deleteLater()


class FlowLayout(QLayout):
    heightChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setSpacing(2)
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
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
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            layout_spacing_y = style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                if isinstance(item.widget(), TagLine):
                    self.heightChanged.emit(y + item.sizeHint().height() + 3)
                    line_rect = QRect(QPoint(x, y), item.sizeHint())
                    line_rect.setRight(rect.right() - space_x)
                    item.setGeometry(line_rect)
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


class TagEdit(QFrame):
    tagChanged = Signal(list)

    def __init__(self, tags: list[str] = None):
        super().__init__(parent=None)
        self.setContentsMargins(3, 1, 3, 1)
        self.setMinimumWidth(200)

        self._tags: dict[str, TagLabel] = dict()
        self.setStyleSheet('TagEdit { '
                           'border-width:0px 0px 1px 0px; '
                           'border-style: solid; '
                           'border-color:gray; '
                           'background-color: white; '
                           '}')

        self._line = TagLine()
        self._line.setMinimumHeight(20)
        self._line.editingFinished.connect(self._append_tag)

        self.setLayout(FlowLayout())
        self.layout().addWidget(self._line)

        self.layout().heightChanged.connect(self.setFixedHeight)

        if tags:
            self.tags = tags

    @property
    def tags(self) -> list[str]:
        return list(self._tags.keys())

    @tags.setter
    def tags(self, tags: list[str]):
        self.clear()
        for tag in tags:
            self._add_tag(tag)

    def set_completer(self, tags: list[str]):
        self._line.set_completer(tags)

    def _append_tag(self):
        tag = self._line.text().strip()
        self._line.clear()
        self._add_tag(tag)

    def _add_tag(self, tag: str):
        if not tag or tag in self._tags:
            return
        tag_label = TagLabel(tag)
        tag_label.deleteTag.connect(self._del_tag)
        self._tags[tag] = tag_label
        self.layout().addWidget(tag_label)
        self.tagChanged.emit(self.tags)

    def _del_tag(self, tag: str):
        self.layout().removeWidget(self._tags.pop(tag))
        self.tagChanged.emit(self.tags)

    def clear(self):
        for tag in self.tags:
            self._tags[tag]._delete()

    def setEnabled(self, enable: bool):
        super().setEnabled(enable)
        self._line.setEnabled(enable)
