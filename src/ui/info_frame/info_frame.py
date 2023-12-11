from PySide6 import QtWidgets, QtCore

from core import functions
from ui.info_frame.tag_edit import TagEdit
from ui.info_frame.year_spin import YearSpin


class InfoFrame(QtWidgets.QFrame):
    infoChanged = QtCore.Signal()

    def __init__(self, session_maker=None):
        super().__init__(parent=None)
        self.setContentsMargins(0, 0, 0, 0)
        self._session = session_maker()
        self._path = ''

        self._tags = TagEdit()
        self._tit = self._create_line('tit')
        self._num = self._create_line('num')
        self._pub = self._create_line('pub')
        self._rls = YearSpin()

        self._tags.setProperty("field", "tags")
        self._rls.setProperty("field", "rls")
        self._rls.setFixedHeight(self._tags.sizeHint().height())

        self.setLayout(QtWidgets.QFormLayout())
        self.layout().addRow("标题", self._tit)
        self.layout().addRow("文号", self._num)
        self.layout().addRow("发布", self._pub)
        self.layout().addRow("年份", self._rls)
        self.layout().addRow("标签", self._tags)

        self._rls.valueChanged.connect(self._change_info)
        self._tags.tagChanged.connect(self._change_info)

        self._reset_completer()
        self.setEnabled(False)

    def _create_line(self, field: str):
        line = QtWidgets.QLineEdit()
        line.setObjectName('LineEdit')
        line.setProperty("field", field)
        line.setContentsMargins(0, 0, 0, 0)
        line.setFixedHeight(self._tags.sizeHint().height())
        line.editingFinished.connect(self._change_info)
        line.data = lambda: line.text()
        return line

    def _get_info(self):
        info = {
            "tit": self._tit.text() if self._tit.text().strip() else None,
            "num": self._num.text() if self._tit.text().strip() else None,
            "pub": self._pub.text() if self._tit.text().strip() else None,
            "rls": self._rls.value(),
            "tags": [functions.get_tag_by_tag(self._session, t) for t in self._tags.tags]
        }
        return info

    def _set_info(self, info: dict):
        self._tit.setText(info.get("tit", ""))
        self._num.setText(info.get("num", ""))
        self._pub.setText(info.get("pub", ""))
        self._rls.setValue(info.get("rls", None))
        self._tags.tags = [t.tag for t in info.get("tags", list())]

    def _change_info(self) -> None:
        pdf = functions.get_pdf_by_path(self._session, self._path)
        if self._tit.text().strip():
            if not pdf:
                pdf = functions.create_pdf_by_path(self._session, self._path)
            field = self.sender().property("field")
            data = self._get_info().get(field)
            functions.update_pdf_with_field(self._session, pdf, field, data)
        else:
            if pdf:
                functions.delete_pdf(self._session, pdf)
            self.clear()
        self.infoChanged.emit()
        self._reset_completer()

    def _reset_completer(self):
        tags = [t.tag for t in functions.get_all_tags(self._session)]
        self._tags.set_completer(tags)

    def set_path(self, path: str):
        self._path = path
        if not self._path:
            self.clear()
            return self.setEnabled(False)
        self.setEnabled(True)
        if pdf := functions.get_pdf_by_path(self._session, self._path):
            info = {k: getattr(pdf, k) for k in ("tit", "num", "pub", "rls", "tags")}
            self._set_info(info)
        else:
            self.clear()

    def clear(self):
        self._tit.clear()
        self._num.clear()
        self._pub.clear()
        self._rls.clear()
        self._tags.clear()
