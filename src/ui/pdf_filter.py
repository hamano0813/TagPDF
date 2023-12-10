import os

from PySide6.QtCore import Qt, QSize, QRect, QPoint, Signal
from PySide6.QtWidgets import QCheckBox, QGroupBox, QPushButton, QFrame, QLayout, QVBoxLayout, QStyle, QSizePolicy

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
        if item in self._item_list:
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
        self.setLayout(FlowLayout())
        self.layout().widthChanged.connect(self.setMinimumWidth)
        self._checks: list[QCheckBox] = list()

    @property
    def selected(self):
        return [check.text() for check in self._checks if check.isChecked()]

    def checks(self):
        return [check.text() for check in self._checks]

    def set_checks(self, checks: list[str], runtime: bool = False):
        for exist_check in self._checks:
            if exist_check.text() not in checks:
                exist_check.stateChanged.disconnect()
                self._checks.remove(exist_check)
                self.layout().removeWidget(exist_check)
                exist_check.deleteLater()
        for check in checks:
            if check not in self.checks():
                self.add_check(check, runtime)

    def add_check(self, check_text: str, checked: bool = False):
        check = QCheckBox(check_text)
        check.setChecked(checked)
        check.stateChanged.connect(self.checkChanged.emit)
        check.setStyleSheet('QCheckBox { padding-left: 5px; padding-right: 5px; }')
        self._checks.append(check)
        self.layout().addWidget(check)

    def clear(self):
        for check in self._checks:
            check.stateChanged.disconnect()
            check.setChecked(False)
            check.stateChanged.connect(self.checkChanged.emit)


class PdfFilter(QFrame):
    filterChanged = Signal(list)

    def __init__(self, session_maker):
        super().__init__(parent=None)
        self.session = session_maker()

        self.pub = CheckGroup("发布")
        self.rel = CheckGroup("年份")
        self.tag = CheckGroup("标签")
        self.export_btn = QPushButton("导出当前列表")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setStyleSheet('QPushButton { font-size: 14px; }')

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 3)
        self.layout().addWidget(self.pub)
        self.layout().addWidget(self.rel)
        self.layout().addWidget(self.tag)
        self.layout().addWidget(self.export_btn)

        self.pub.checkChanged.connect(self.check_changed)
        self.rel.checkChanged.connect(self.check_changed)
        self.tag.checkChanged.connect(self.check_changed)

    def check_changed(self):
        publisher = self.pub.selected
        release = list(map(int, self.rel.selected))
        tags = self.tag.selected
        pdfs = self.session.query(PDF).filter(
            PDF.pub.in_(publisher) if publisher else True,
            PDF.rls.in_(release) if release else True,
            PDF.tags.any(TAG.tag.in_(tags)) if tags else True,
        ).all()
        paths = []
        for pdf in pdfs:
            if os.path.exists(pdf.fp):
                paths.append(pdf.fp)
            else:
                self.session.delete(pdf)
        self.filterChanged.emit(paths)

    def refresh(self, runtime: bool = False):
        self.pub.set_checks(
            [i[0] for i in self.session.query(PDF.pub).distinct().order_by(PDF.pub) if i[0]], runtime)
        self.rel.set_checks(
            [str(i[0]) for i in self.session.query(PDF.rls).distinct().order_by(PDF.rls) if i[0]], runtime)
        self.tag.set_checks([i[0] for i in self.session.query(TAG.tag).filter(TAG.pdf).distinct().order_by(TAG.tag)],
                            runtime)

    def clear(self):
        self.pub.clear()
        self.rel.clear()
        self.tag.clear()
