import pdb
from math import floor
from PyQt5.QtWidgets import (QWidget, QDockWidget, QTabWidget, QLabel,
							QPushButton, QHBoxLayout, QVBoxLayout,
							QGraphicsOpacityEffect, QSizePolicy,
							QToolBar, QScrollArea, QDialog, QGridLayout,
							QCheckBox, QLineEdit)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont, QImage, QPixmap, QIntValidator
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from crawler.project_vars import Paths, Spiders
from tile_layout import TileLayout
from crawler.settings import load_settings, save_settings

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'

def initialize_animation(obj):
	# Create an opacity animation that can be started later:
	# Set up the fade in animation now, initiate later:
	opacity = QGraphicsOpacityEffect()
	opacity.setOpacity(0)
	obj.setGraphicsEffect(opacity)

	obj.opacity_animation = QPropertyAnimation(obj.graphicsEffect(), "opacity".encode())
	obj.opacity_animation.setDuration(200)
	obj.opacity_animation.setStartValue(0)
	obj.opacity_animation.setEndValue(1)

	obj.delay = QTimer()
	obj.delay.setSingleShot(True)
	obj.delay.timeout.connect(obj.opacity_animation.start)

# Thumbnail class that can be used to create images with given geometry
class Thumbnail(QLabel):

	# maintain_aspect_ratio: Keep aspect ratio when resizing

	def __init__(self, **kwargs):
		super(Thumbnail, self).__init__()
		data = kwargs["data"]
		self.app = kwargs["app"]
		self.maintain_aspect_ratio = data["maintain_aspect_ratio"]

		self.geometry_target = data["geometry_target"]

		self.image = QImage()
		self.image.load(data["image"])

		self.src = data["source"]

		self.resize(self.geometry_target)
		self.setPixmap(QPixmap.fromImage(self.image))

		# This function sets the size hint to its contents
		self.adjustSize()

		# The horizontal size is left unconstrained, and
		# handled instead by the layout
		self.sizePolicy().setHorizontalPolicy(5)

		# In the veritcal direction, we do not let the height change
		# from that needed to display
		self.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
	


	def resize(self, geometry_target):

		if self.maintain_aspect_ratio:
			self.image = self.image.scaled(QSize(geometry_target[0],
												geometry_target[1]),
						aspectRatioMode = Qt.KeepAspectRatio)
		else:
			self.image = self.image.scaled(QSize(geometry_target[0],
												 geometry_target[1]),
						 aspectRatioMode = Qt.IgnoreAspectRatio)

	# When clicked, tell the app to switch to the corresponding source
	def mousePressEvent(self, event):

		self.app.switch_to_source(self.src)



class DockWidget(QDockWidget):

	def __init__(self, app):
		super(DockWidget, self).__init__()
		self.app = app
		self.topLevelChanged.connect(self.handoff_float)

		toolbar = QToolBar()

		self.full_screen_btn = QPushButton("Full Screen")
		self.full_screen_btn.clicked.connect(self.full_screen)

		self.exit_full_screen_btn = QPushButton("Exit Full Screen")
		self.exit_full_screen_btn.clicked.connect(self.exit_full_screen)

		toolbar.addWidget(self.full_screen_btn)

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

	def full_screen(self):
	# Make the dock take up the whole screen:
	# Hide the content area widget:


		# Record the dock widget's width as a fraction of the window
		# width so that we can restore it when exiting full screen mode

		self.docked_width = self.width()/self.app.width()

		self.app.content_area_widget.hide()

		target_geometry = QRect(self.app.geometry().x(),
								self.app.geometry().y(),
								self.app.width(),
								self.height())
		self.setGeometry(target_geometry)

		toolbar = QToolBar()
		toolbar.addWidget(self.exit_full_screen_btn)

		self.setTitleBarWidget(toolbar)

	def exit_full_screen(self):
	# Restore the dock widget to its previous configuration

		toolbar = QToolBar()
		toolbar.addWidget(self.full_screen_btn)

		self.setTitleBarWidget(toolbar)

		self.app.content_area_widget.show()

		# For some reason, we have to use resizeDocks when existing full screen
		# or else it won't work
		self.app.resizeDocks([self], [self.docked_width * self.app.width()],\
							 Qt.Horizontal)

	def closeEvent(self, event):
		self.app.ntabs = 0
		super(DockWidget, self).closeEvent(event)

	# Convenience method to do the same thing as closeEvent but from 
	# outside of Qt event system
	def close(self):
		self.app.ntabs = 0
		target_geometry = QRect(self.app.geometry().x(),
								self.app.geometry().y(),
								self.app.width(),
								self.height())
		self.app.content_area_widget.resize(target_geometry)

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
			dock_widget.close()
			dock_widget.setParent(None)



class Content_Area_Widget(QWidget):

	def __init__(self, app):
		super(Content_Area_Widget, self).__init__()
		self.app = app

	def resize(self, target_geometry):
		target_width = target_geometry.width()
		# Collect all tile_layouts:
		tile_layouts = self.findChildren(TileLayout)

		self.setGeometry(target_geometry)

		for tile_layout in tile_layouts:

			if target_width > tile_layout.max_width or\
				target_width < tile_layout.min_width:
				tile_layout.redraw(target_width)
			else:
				tile_layout.adjust(target_width)

	def restore(self):
		if self.app.active_source is not None:
			self.setGeometry()



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
		article = kwargs["data"]
		self.setAttribute(Qt.WA_AcceptTouchEvents, on = True)

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

		title.setAttribute(Qt.WA_AcceptTouchEvents, on = True)

		tile_layout.addWidget(title)


		secondary_text = "By %s" % self.authors
		secondary_text += "| "
		secondary_text += self.tags

		secondary_text = QLabel(secondary_text)

		secondary_text.setWordWrap(True)
		secondary_text.adjustSize()
		secondary_text.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)
		secondary_text.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
		secondary_text.setAttribute(Qt.WA_AcceptTouchEvents, on = True)

		tile_layout.addWidget(secondary_text)
		PDF_link = QPushButton("PDF")
		PDF_link.clicked.connect(self.open_pdf)
		PDF_link.setAttribute(Qt.WA_AcceptTouchEvents, on = True)

		tile_layout.addWidget(PDF_link)
	
		desc = QLabel(self.desc)
		desc.setWordWrap(True)
		desc.adjustSize()
		desc.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)
		desc.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
		desc.setAttribute(Qt.WA_AcceptTouchEvents, on = True)
		tile_layout.addWidget(desc)

		self.setLayout(tile_layout)

		# Resize to fit children
		self.adjustSize()

		# Mirror size policy of children
		self.sizePolicy().setVerticalPolicy(QSizePolicy.Minimum)
		self.sizePolicy().setHorizontalPolicy(QSizePolicy.Preferred)

	def open_pdf(self):
		file_path = Paths.files_path + self.path
#			os.startfile(file_path)
	
		self.app_window.add_pdf_dock(file_path)

class SettingsDialog(QDialog):

	def __init__(self, **kwargs):
		super(SettingsDialog, self).__init__()
		self.app = kwargs["app"]
		app_geom = self.app.geometry()
		width = 500
		height = 500

		x = (app_geom.width() - width)/2
		y = (app_geom.height() - height)/2

		self.setGeometry(x, y, width, height)
		self.layout = QGridLayout()

		# Dictionary of settings values loaded in from file
		self.settings = load_settings()
		# Table headers
		self.layout.addWidget(QLabel("Enabled"), 0, 1)
		self.layout.addWidget(QLabel("Sync Back For (days)"), 0, 2)

		# Create settings widgets and initialize to default values
		for i, src in enumerate(Spiders.spiders):

			self.layout.addWidget(QLabel(Spiders.spider_names[i]),\
											i+1, 0)
			chkbox = QCheckBox("")
			chkbox.setObjectName(src)
			chkbox.setChecked(self.settings[src]["enabled"])
			self.layout.addWidget(chkbox, i + 1, 1)
			
			dayinput = QLineEdit()
			dayinput.setObjectName(src)
			day_validator = QIntValidator(0, Spiders.max_range[i])
			dayinput.setValidator(day_validator)
			dayinput.setText(self.settings[src]["sync_length"])
			# Hovering over the input will show the maximum range
			dayinput.setToolTip("Max: %d days" % Spiders.max_range[i])


			self.layout.addWidget(dayinput, i + 1, 2)

		accept_button = QPushButton('OK')
		accept_button.setDefault(True)
		accept_button.clicked.connect(self.accept)


		self.layout.addWidget(accept_button, len(Spiders.spiders) + 2, 1)

		self.setWindowTitle('Crawler Settings')
		self.setLayout(self.layout)
		# This will prevent user from doing anything until the dialog has 
		# been dismissed
		self.setWindowModality(Qt.ApplicationModal)

	def accept(self):
		# Read out values of all fields:
		for src in Spiders.spiders:
			self.settings[src]["enabled"] = self.findChild(QCheckBox, src).isChecked()
			self.settings[src]["sync_length"] = self.findChild(QLineEdit, src).text()

		save_settings(self.settings)
		self.done(1)