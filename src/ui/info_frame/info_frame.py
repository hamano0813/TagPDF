from PySide6 import QtWidgets, QtCore

from .tag_edit import TagEdit
from .year_spin import YearSpin
from core import functions


class InfoFrame(QtWidgets.QFrame):
    infoChanged = QtCore.Signal()

    def __init__(self, session_maker=None):
        super().__init__(parent=None)
        self.setContentsMargins(0, 0, 0, 0)
        self.session = session_maker()
        self.path = ''

        self.tags = TagEdit()
        self.tags.setProperty("field", "tags")
        self.tit = self._create_line('tit')
        self.num = self._create_line('num')
        self.pub = self._create_line('pub')
        self.rls = YearSpin()
        self.rls.setProperty("field", "rls")
        self.rls.setFixedHeight(self.tags.sizeHint().height())

        self.setLayout(QtWidgets.QFormLayout())
        self.layout().addRow("标题", self.tit)
        self.layout().addRow("文号", self.num)
        self.layout().addRow("发布", self.pub)
        self.layout().addRow("年份", self.rls)
        self.layout().addRow("标签", self.tags)

        self.rls.valueChanged.connect(self.change_info)
        self.tags.tagChanged.connect(self.change_info)

        self.refresh_completer()

    def _create_line(self, field: str):
        line = QtWidgets.QLineEdit()
        line.setObjectName('LineEdit')
        line.setProperty("field", field)
        line.setContentsMargins(0, 0, 0, 0)
        line.setFixedHeight(self.tags.sizeHint().height())
        line.editingFinished.connect(self.change_info)
        line.data = lambda: line.text()
        return line

    def get_info(self):
        info = {
            "tit": self.tit.text() if self.tit.text().strip() else None,
            "num": self.num.text() if self.tit.text().strip() else None,
            "pub": self.pub.text() if self.tit.text().strip() else None,
            "rls": self.rls.value(),
            "tags": [functions.get_tag_by_tag(self.session, t) for t in self.tags.tags]
        }
        return info

    def set_info(self, info: dict):
        self.tit.setText(info.get("tit", ""))
        self.num.setText(info.get("num", ""))
        self.pub.setText(info.get("pub", ""))
        self.rls.setValue(info.get("rls", None))
        self.tags.tags = [t.tag for t in info.get("tags", list())]

    def change_info(self) -> None:
        if not self.path:
            return self.sender().clear()
        if not (pdf := functions.get_pdf_by_path(self.session, self.path)):
            pdf = functions.create_pdf_by_path(self.session, self.path)
        field = self.sender().property("field")
        data = self.get_info().get(field)
        if self.get_info().get("tit"):
            functions.update_pdf_with_field(self.session, pdf, field, data)
        else:
            functions.delete_pdf(self.session, pdf)
            self.clear()
        self.infoChanged.emit()
        self.refresh_completer()

    def clear(self):
        self.tit.clear()
        self.num.clear()
        self.pub.clear()
        self.rls.clear()
        self.tags.clear()

    def set_path(self, path: str):
        self.path = path
        if pdf := functions.get_pdf_by_path(self.session, self.path):
            info = {k: getattr(pdf, k) for k in ("tit", "num", "pub", "rls", "tags")}
            self.set_info(info)
        else:
            self.clear()

    def refresh_completer(self):
        tags = [t.tag for t in functions.get_all_tags(self.session)]
        self.tags.set_completer(tags)
