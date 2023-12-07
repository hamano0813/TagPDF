from typing import Optional

from PySide6.QtCore import Signal, QMetaMethod
from PySide6.QtWidgets import QFrame, QLineEdit, QFormLayout

from core.model import PDF, TAG
from .tag_edit import TagEdit
from .year_spin import YearSpin


class InfoEditor(QFrame):
    infoChanged = Signal()

    def __init__(self, parent=None, session_maker=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.session = session_maker()
        self.path = ''
        self.pdf: Optional[PDF] = None

        self.title = QLineEdit()
        self.publisher = QLineEdit()
        self.release = YearSpin()
        self.tags = TagEdit()

        self.title.setFixedHeight(30)
        self.publisher.setFixedHeight(30)
        self.release.setFixedHeight(30)
        self.title.setStyleSheet('QLineEdit { padding-left: 3px; padding-right: 3px; }')
        self.publisher.setStyleSheet('QLineEdit { padding-left: 3px; padding-right: 3px; }')
        self.title.setContentsMargins(0, 0, 0, 0)
        self.publisher.setContentsMargins(0, 0, 0, 0)
        self.release.setContentsMargins(0, 0, 0, 0)
        self.tags.setContentsMargins(0, 0, 0, 0)

        self.setLayout(QFormLayout())
        self.layout().addRow(self.tr("Title"), self.title)
        self.layout().addRow(self.tr("Publisher"), self.publisher)
        self.layout().addRow(self.tr("Release"), self.release)
        self.layout().addRow(self.tr("Tags"), self.tags)

        self._enable(False)
        self._connect()
        self.refresh_completer()

    def _enable(self, enable: bool):
        self.publisher.setReadOnly(not enable)
        self.release.setEnabled(enable)
        self.tags.setEnabled(enable)

    def _connect(self):
        self.title.editingFinished.connect(self.title_changed)
        self.publisher.editingFinished.connect(self.publisher_changed)
        self.release.valueChanged.connect(self.release_changed)
        self.tags.tagChanged.connect(self.tags_changed)

    def clear(self):
        self.title.clear()
        self.publisher.clear()
        self.release.clear()
        self.tags.clear()

    def set_path(self, path: str):
        self.path = path
        self.pdf = self.session.query(PDF).filter(PDF.fp == path).one_or_none()
        if self.pdf:
            self.title.setText(self.pdf.title)
            self.publisher.setText(self.pdf.publisher)
            self.release.setValue(self.pdf.release)
            self.tags.tags = [t.tag for t in self.pdf.tags]
            self._enable(True)
        else:
            self.clear()
            self._enable(False)

    def title_changed(self):
        if title := self.title.text().strip():
            if not self.pdf and self.path:
                self.pdf = PDF(fp=self.path)
                self._enable(True)
                self.pdf.title = title
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
        if publisher := self.publisher.text().strip():
            self.pdf.publisher = publisher
            self.session.add(self.pdf)
            self.session.commit()
        else:
            self.pdf.publisher = None
            self.session.add(self.pdf)
            self.session.commit()
        self.infoChanged.emit()

    def release_changed(self):
        if not self.pdf:
            return
        self.pdf.release = self.release.value()
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
        self.refresh_completer()

    def refresh_completer(self):
        all_tags = {t.tag: t for t in self.session.query(TAG).all()}
        self.tags.set_completer([t.tag for t in all_tags.values()])
