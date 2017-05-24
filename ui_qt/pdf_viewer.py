import sys
import os
from math import ceil, floor
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout, QMainWindow, QToolBar,
							 QSizePolicy, QGraphicsOpacityEffect, QDockWidget)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.QAxContainer import QAxWidget
import pdb

class PDFViewerContainer(QWidget):

	def __init__(self, pdf_path):
		super(PDFViewerContainer, self).__init__()

		container_layout = QVBoxLayout()
		container_layout.addWidget(self.make_toolbar())

		self.pdf_viewer = PDF_Viewer()
		self.pdf_viewer.set_pdf(pdf_path)
		container_layout.addWidget(self.pdf_viewer)
		self.setLayout(container_layout)


	def make_toolbar(self):
		toolbar = QToolBar()
		toolbar.setFloatable = False
		toolbar.setMovable = False
		toolbar.addWidget(QLabel("Hello!"))
		return toolbar

class PDF_Viewer(QAxWidget):
	# Need to install Adobe PDF Viewer for this to work
	def __init__(self):
		super(PDF_Viewer, self).__init__()
		self.setControl('AcroPDF.PDF')
	def set_pdf(self, pdf_path):
		self.dynamicCall("LoadFile(const QString)", pdf_path)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	root_widget = PDF_Viewer()
	root_widget.show()
	sys.exit(app.exec_())