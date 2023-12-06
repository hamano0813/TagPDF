from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView


class PdfView(QPdfView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocument(QPdfDocument(self))
        self.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.setPageMode(QPdfView.PageMode.MultiPage)
