import os

from PySide6.QtWidgets import QCheckBox, QGroupBox, QPushButton, QFrame, QLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QSize, QRect, QPoint, Signal

from core.model import PDF, TAG


class FlowLayout(QLayout):
    widthChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(3)
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

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
        size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return size

    def _do_layout(self, rect, test_only):
        line_height = 0
        spacing = self.spacing()
        x = rect.x() + spacing
        y = rect.y() + spacing
        for item in self._item_list:
            style: QStyle = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
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
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        if self.count():
            self.widthChanged.emit(max(i.widget().width() for i in self._item_list) + spacing * 2)
        return y + line_height - rect.y()


class CheckGroup(QGroupBox):
    checkChanged = Signal(bool)

    def __init__(self, title):
        super().__init__(title, parent=None)
        self.setTitle(title)
        self._layout = FlowLayout()
        self.setLayout(self._layout)
        self._layout.widthChanged.connect(self.setMinimumWidth)
        self._checks: list[QCheckBox] = list()

    @property
    def checks(self):
        return [check.text() for check in self._checks if check.isChecked()]

    @checks.setter
    def checks(self, tags: list[str]):
        self.clear()
        for tag in tags:
            self.add_check(tag)

    def set_checks(self, tags: list[str]):
        current_checks = {check.text(): check for check in self._checks}
        for check_tag, check in current_checks.items():
            if check_tag not in tags:
                check.stateChanged.disconnect()
                self._layout.removeItem(check)
                check.deleteLater()
        for tag in tags:
            if tag not in current_checks:
                self.add_check(tag, True)

    def add_check(self, text, default=False):
        check = QCheckBox(text)
        check.setChecked(default)
        check.stateChanged.connect(self.checkChanged.emit)
        check.setStyleSheet('QCheckBox { padding-left: 5px; padding-right: 5px; }')
        self._checks.append(check)
        self._layout.addWidget(check)

    def clear(self):
        for check in self._checks:
            check.stateChanged.disconnect()
            self._layout.removeWidget(check)
            check.deleteLater()
        self._checks.clear()
        self.checkChanged.emit(True)


class CheckFilter(QFrame):
    selectChanged = Signal(list)

    def __init__(self, session_maker):
        super().__init__(parent=None)
        self.session = session_maker()

        self.publisher_group = CheckGroup("发布")
        self.release_group = CheckGroup("年份")
        self.tags_group = CheckGroup("标签")
        self.export_btn = QPushButton("导出当前列表")
        self.export_btn.setFixedHeight(50)

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.publisher_group)
        self.layout().addWidget(self.release_group)
        self.layout().addWidget(self.tags_group)
        self.layout().addWidget(self.export_btn)

        self.publisher_group.checkChanged.connect(self.check_changed)
        self.release_group.checkChanged.connect(self.check_changed)
        self.tags_group.checkChanged.connect(self.check_changed)

    def check_changed(self):
        publisher = self.publisher_group.checks
        release = [int(r) for r in self.release_group.checks]
        tags = self.tags_group.checks
        pdfs = self.session.query(PDF).filter(
            PDF.publisher.in_(publisher) if publisher else True,
            PDF.release.in_(release) if release else True,
            PDF.tags.any(TAG.tag.in_(tags)) if tags else True,
        ).all()
        paths = []
        for pdf in pdfs:
            if os.path.exists(pdf.fp):
                paths.append(pdf.fp)
            else:
                self.session.delete(pdf)
        self.selectChanged.emit(paths)

    def refresh_publisher(self):
        self.publisher_group.checks = [
            i[0] for i in self.session.query(PDF.publisher).distinct().order_by(PDF.publisher) if i[0]
        ]

    def refresh_release(self):
        self.release_group.checks = [
            str(i[0]) for i in self.session.query(PDF.release).distinct().order_by(PDF.release) if i[0]
        ]

    def refresh_tags(self):
        self.tags_group.checks = [
            i[0] for i in self.session.query(TAG.tag).distinct().order_by(TAG.tag) if i[0]
        ]

    def refresh(self):
        self.refresh_publisher()
        self.refresh_release()
        self.refresh_tags()

    def runtime_refresh(self):
        publisher = [i[0] for i in self.session.query(PDF.publisher).distinct().order_by(PDF.publisher) if i[0]]
        release = [str(i[0]) for i in self.session.query(PDF.release).distinct().order_by(PDF.release) if i[0]]
        tags = [i[0] for i in self.session.query(TAG.tag).distinct().order_by(TAG.tag) if i[0]]

        self.publisher_group.set_checks(publisher)
        self.release_group.set_checks(release)
        self.tags_group.set_checks(tags)
