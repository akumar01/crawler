from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
import pdb

class PDFViewer(QWebEngineView):
    pdf_viewer_page = 'pdftest/res/pdf-viewer.html'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QWebEngineSettings.globalSettings()
        self.settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True )
        self.settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True )
#        self.settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True )
#        nam = QNetworkAccessManager()
        page = QWebEnginePage(self)
#        page.setNetworkAccessManager(nam)
        self.setPage(page)
        self.loadFinished.connect(self.onLoadFinish)
        self.setUrl(QUrl(self.pdf_viewer_page))

    def onLoadFinish(self, success):
        if success:
            self.page().mainFrame().evaluateJavaScript("init();")


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    viewer = PDFViewer(parent=None)
    viewer.show()
    sys.exit(app.exec_())