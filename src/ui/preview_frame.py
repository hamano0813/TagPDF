from PySide6 import QtPdf, QtPdfWidgets


class PreviewFrame(QtPdfWidgets.QPdfView):
    def __init__(self):
        super().__init__()
        self.setDocument(QtPdf.QPdfDocument(self))
        self.setZoomMode(QtPdfWidgets.QPdfView.ZoomMode.FitToWidth)
        self.setPageMode(QtPdfWidgets.QPdfView.PageMode.MultiPage)

    def set_path(self, path: str):
        document = QtPdf.QPdfDocument(self)
        if path:
            document.load(path)
        else:
            self.document().close()
            self.document().deleteLater()
        self.setDocument(document)