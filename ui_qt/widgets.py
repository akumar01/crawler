import pdb
from PyQt5.QtWidgets import (QWidget, QDockWidget, QTabWidget, QLabel,
							QPushButton, QHBoxLayout, QVBoxLayout,
							QGraphicsOpacityEffect, QSizePolicy)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from crawler.project_vars import Paths, Spiders

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'


class DockWidget(QDockWidget):

	def __init__(self, app):
		super(DockWidget, self).__init__()
		self.app = app
		self.topLevelChanged.connect(self.handoff_float)

		toolbar = QToolBar()
		full_screen = QB
		toolbar.addWidget(QPushButton('Full Screen'))

		self.setTitleBarWidget(toolbar)

	def resizeEvent(self, event):
	# If we change the size of the dock widget, then the content_area_widget 
	# needs to be resized appropriately
		target_geometry = QRect(self.app.centralWidget().x(),
								self.app.centralWidget().y(),
								self.app.width() - self.width(),
								self.app.centralWidget().height())
		self.app.content_area_widget.resize(target_geometry)

	def handoff_float(self, floating):
		if floating:
			target_geometry = QRect(self.app.centralWidget().x(),
									self.app.centralWidget().y(),
									self.app.width(),
									self.app.centralWidget().height())
		else:
			target_geometry = QRect(self.app.centralWidget().x(),
									self.app.centralWidget().y(),
									self.app.width() - self.width(),
									self.app.centralWidget().height())

		self.app.content_area_widget.resize(target_geometry)

	def closeEvent(self, event):
		self.app.ntabs = 0
		super(DockWidget, self).closeEvent(event)

class TabWidget(QTabWidget):

	def __init__(self, app):
		super(TabWidget, self).__init__()
		self.setMovable(True)
		self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_tab)
		self.app = app

	def close_tab(self, index):
		self.app.ntabs -= 1
		tab = self.widget(index)
		self.removeTab(index)
		tab.setParent(None)

		# Close the dock widget if we have closed all tabs:
		if self.app.ntabs == 0:
			dock_widget = self.app.findChildren(DockWidget)[0]
			self.app.removeDockWidget(dock_widget)
			dock_widget.setParent(None)


class Content_Area_Widget(QWidget):

	def __init__(self, app):
		super(Content_Area_Widget, self).__init__()
		self.app = app

	def resize(self, target_geometry):
		target_width = target_geometry.width()

		if self.app.active_source is None:
			return
		else:
			self.setGeometry(target_geometry)
			# If the widget has only been resized by +- 1, it is 
			# due to the resize_kludge and it is important that we 
			# do nothing in response
			if target_width > self.app.max_width or\
				target_width < self.app.min_width:
				self.app.redraw_source()
			else:
				self.app.adjust_source()


class SourceSelector(QLabel):

	def __init__(self, text, **kwargs):
		super(SourceSelector, self).__init__(text)
		self.app = kwargs["app"]
		self.source = kwargs["source"]

	def mousePressEvent(self, event):
		self.app.switch_to_source(self.source)

class BackButton(QPushButton):

	def __init__(self, text, **kwargs):
		super(BackButton, self).__init__(text)
		self.app = kwargs["app"]

	def mousePressEvent(self, event):
		self.app.return_home()

class SourceTile(QWidget):

	def __init__(self, **kwargs):
		super(SourceTile, self).__init__()

		tile_layout = QVBoxLayout()
		self.app_window = kwargs["app"]
		article = kwargs["article"]

		self.title = article["title"]
		self.authors = article["authors"]
		self.tags = article["tags"]
#		self.desc = article["desc"]
		self.desc = lorem_ipsum
		self.path = article["files"][0]["path"]

		self.column = 0

		title = QLabel(self.title)

		# Set Font size to 18pt for article title.
		title.setFont(QFont("Helvetica", 18))


		# Wrap if title is too long
		title.setWordWrap(True)

		# This function sets the size hint to its contents
		title.adjustSize()

		# Set the title sizepolicy. The horizontal size is left
		# unconstrained, and handled instead by the layout
		title.sizePolicy().setHorizontalPolicy(5)

		# In the veritcal direction, we do not let the height change
		# from that needed to display
		title.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)


		tile_layout.addWidget(title)


		secondary_text = "By %s" % self.authors
		secondary_text += "| "
		secondary_text += self.tags

		secondary_text = QLabel(secondary_text)

		secondary_text.setWordWrap(True)
		secondary_text.adjustSize()
		secondary_text.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)
		secondary_text.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)

		tile_layout.addWidget(secondary_text)
		PDF_link = QPushButton("PDF")
		PDF_link.clicked.connect(self.open_pdf)
		tile_layout.addWidget(PDF_link)
	
		desc = QLabel(self.desc)
		desc.setWordWrap(True)
		desc.adjustSize()
		desc.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)
		desc.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
		tile_layout.addWidget(desc)

		self.setLayout(tile_layout)

		# Resize to fit children
		self.adjustSize()

		# Mirror size policy of children
		self.sizePolicy().setVerticalPolicy(QSizePolicy.Minimum)
		self.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)


	def initialize_animation(self):
		# Create an opacity animation that can be started later:
		# Set up the fade in animation now, initiate later:
		opacity = QGraphicsOpacityEffect()
		opacity.setOpacity(0)
		self.setGraphicsEffect(opacity)

		self.opacity_animation = QPropertyAnimation(self.graphicsEffect(), "opacity".encode())
		self.opacity_animation.setDuration(200)
		self.opacity_animation.setStartValue(0)
		self.opacity_animation.setEndValue(1)

		self.delay = QTimer()
		self.delay.setSingleShot(True)
		self.delay.timeout.connect(self.opacity_animation.start)




	def open_pdf(self):
		file_path = Paths.files_path + self.path
#			os.startfile(file_path)
	
		self.app_window.add_pdf_dock(file_path)
