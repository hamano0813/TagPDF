from PySide6 import QtPdf, QtPdfWidgets


class PreviewFrame(QtPdfWidgets.QPdfView):
    def __init__(self):
        super().__init__()
        self._document = None
        self.setZoomMode(QtPdfWidgets.QPdfView.ZoomMode.FitToWidth)
        self.setPageMode(QtPdfWidgets.QPdfView.PageMode.MultiPage)

    def set_path(self, path: str):
        if not self._document:
            self._document = QtPdf.QPdfDocument(self)
        else:
            self._document.close()
        if path:
            self._document.load(path)
        self.setDocument(self._document)
