from PySide6 import QtWidgets, QtCore

from core.model import PDF, TAG
from .tag_edit import TagEdit
from .year_spin import YearSpin


class InfoFrame(QtWidgets.QFrame):
    infoChanged = QtCore.Signal()

    def __init__(self, session_maker=None):
        super().__init__(parent=None)
        self.setContentsMargins(0, 0, 0, 0)
        self.session = session_maker()
        self.path = ''
        self.pdf: PDF | None = None

        self.tags = TagEdit()
        self.tit = self._create_line()
        self.num = self._create_line()
        self.pub = self._create_line()
        self.rls = YearSpin()
        self.rls.setFixedHeight(self.tags.sizeHint().height())

        self.setLayout(QtWidgets.QFormLayout())
        self.layout().addRow("标题", self.tit)
        self.layout().addRow("文号", self.num)
        self.layout().addRow("发布", self.pub)
        self.layout().addRow("年份", self.rls)
        self.layout().addRow("标签", self.tags)

        self._enable(False)
        self._connect()
        self.refresh_completer()

    def _create_line(self):
        line = QtWidgets.QLineEdit()
        line.setObjectName('LineEdit')
        line.setContentsMargins(0, 0, 0, 0)
        line.setFixedHeight(self.tags.sizeHint().height())
        return line

    def _enable(self, enable: bool):
        self.pub.setReadOnly(not enable)
        self.rls.setEnabled(enable)
        self.tags.setEnabled(enable)

    def _connect(self):
        self.tit.editingFinished.connect(self.title_changed)
        self.pub.editingFinished.connect(self.publisher_changed)
        self.rls.valueChanged.connect(self.release_changed)
        self.tags.tagChanged.connect(self.tags_changed)

    def clear(self):
        self.tit.clear()
        self.pub.clear()
        self.rls.clear()
        self.tags.clear()

    def set_path(self, path: str):
        self.path = path
        self.pdf = self.session.query(PDF).filter(PDF.fp == path).one_or_none()
        if self.pdf:
            self._enable(True)
            self.tit.setText(self.pdf.tit)
            self.pub.setText(self.pdf.pub)
            self.rls.setValue(self.pdf.rls)
            self.tags.tags = [t.tag for t in self.pdf.tags]
        else:
            self.clear()
            self._enable(False)

    def title_changed(self):
        if title := self.tit.text().strip():
            if not self.pdf and self.path:
                self.pdf = PDF(fp=self.path)
                self._enable(True)
                self.pdf.tit = title
                self.session.add(self.pdf)
                self.session.commit()
            else:
                self.pdf.tit = title
                self.session.add(self.pdf)
                self.session.commit()
        elif self.pdf:
            self.clear()
            self._enable(False)
            self.session.delete(self.pdf)
            self.session.commit()
            self.pdf = None
        self.infoChanged.emit()

    def publisher_changed(self):
        if not self.pdf:
            return
        if publisher := self.pub.text().strip():
            self.pdf.pub = publisher
            self.session.add(self.pdf)
            self.session.commit()
        else:
            self.pdf.pub = None
            self.session.add(self.pdf)
            self.session.commit()
        self.infoChanged.emit()

    def release_changed(self):
        if not self.pdf:
            return
        self.pdf.rls = self.rls.value()
        self.session.add(self.pdf)
        self.session.commit()
        self.infoChanged.emit()

    def tags_changed(self):
        if not self.pdf:
            return
        all_tags = {t.tag: t for t in self.session.query(TAG).all()}
        pdf_tags = {t.tag: t for t in self.pdf.tags}
        use_tags = self.tags.tags
        for tag in use_tags:
            if tag not in all_tags:
                all_tags[tag] = TAG(tag=tag)
            if tag not in pdf_tags:
                self.pdf.tags.append(all_tags[tag])
        for tag in pdf_tags:
            if tag not in use_tags:
                self.pdf.tags.remove(pdf_tags[tag])
        self.session.add(self.pdf)
        self.session.commit()
        self.infoChanged.emit()
        self.refresh_completer()

    def refresh_completer(self):
        all_tags = {t.tag: t for t in self.session.query(TAG).all()}
        self.tags.set_completer([t.tag for t in all_tags.values()])
