from PySide6 import QtPdf, QtPdfWidgets


class PreviewFrame(QtPdfWidgets.QPdfView):
    def __init__(self):
        super().__init__()
        self._document = None
        self.setZoomMode(QtPdfWidgets.QPdfView.ZoomMode.FitToWidth)
        self.setPageMode(QtPdfWidgets.QPdfView.PageMode.MultiPage)

    def set_path(self, path: str):
        if self._document:
            self._document.close()
            self._document.deleteLater()
            self._document = None
        self._document = QtPdf.QPdfDocument(self)
        if path:
            self._document.load(path)
        self.setDocument(self._document)
