import pdb
from PyQt5.QtWidgets import (QWidget, QDockWidget, QTabWidget, QLabel,
							QPushButton, QHBoxLayout, QVBoxLayout,
							QGraphicsOpacityEffect, QSizePolicy,
							QToolBar, QScrollArea)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from crawler.project_vars import Paths, Spiders

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'

class TileLayout(QScrollArea):

	def __init__(self, app, geometry_type):
		super(TileLayout, self).__init__()
		self.app = app

		self.setAttribute(Qt.WA_AcceptTouchEvents, on = True)

		# Container widget
		self.source_grid_container = QWidget()

		# To achive a tile layout like functionality, we arrange vertical
		# box layouts in a horizontal box layout

		self.source_columns = QHBoxLayout()
		self.geometry_params = geometry_params
		self.init_geometry(geometry_params)

	# Setup basic layout parameters
	def init_geometry(self, geometry_params):

		# Calculate the available width from the width and the margins.
		# This calculation is ported over from kivy TileLayout

		self.spacing_x = geometry_params["tile_spacing_x"]
		self.padding_x = geometry_params["tile_area_margin_x"]

		self.available_width = geometry_params["central_widget_width"] -\
							2 * padding_x

		self.n_tiles_across =  max(1, int(floor((available_width + spacing_x)/
										(self.target_dim + spacing_x))))

		# Tile width is always the target dim
		self.tile_width = geometry_params["target_dim"]
		# Add extra space to the margins
		padding_x += (available_width/n_tiles_across - tile_width)/2

		# If the window is made wider than the width of an additional tile
		# plus the spacing, then redraw:
		self.max_width = available_width + self.target_dim + spacing_x

		# If the window is made smaller to the point that the tile_width would 
		# have to be reduced to below the target_dim, then redraw: 
		self.min_width = max(0, available_width -\
						(n_tiles_across * (tile_width - self.target_dim))) 


	# Assign information necessary to create children to the TileLayout
	# children_cls determines which class to make the children out of 
	def set_children(self, children, children_cls):

		self.tiles = []
		self.total_height_needed = 0

		for child in children:
			tile = children_cls(data = child, app = self.app)
			tile.setFixedWidth(self.tile_width)
			self.total_height_neeeded += tile.heightForWidth(self.tile_width)
			self.tiles.append(tile)

		self.avg_height = float(self.total_height_neeeded)/self.n_tiles_across

	# Call after children have been correctly assigned to actually sort them 
	# into the appropriate columns
	def arrange_layout(self):

		tiles = self.tiles
		n_tiles_across = self.n_tiles_across
		avg_height = self.avg_height

		# Which stack should the child be added to?
		stack = [0] * len(tiles)

		# stack_ind goes from 0 to n_tiles_across - 1
		stack_ind = 0

		# How high is each stack?
		stack_heights = [0] * n_tiles_across

		# How many tiles are in each stack? 
		stack_occupancy = [0] * n_tiles_across

		# We want to assign each child to a stack. The reason this is
		# not so straightforward is that we want to add entries left 
		# to right, but it is the vertical height we want to take care of.
		# Thus, do the following: iterate through children left to right and
		# as long as the the current stack height does not exceed the average 
		# height, add it. If the current stack is filled up, then shift one 
		# over until we find the first available stack.

		for i in range(len(tiles)):
			if stack_heights[stack_ind] <= avg_height:
				stack[i] = stack_ind
				stack_heights[stack_ind] += tiles[i].heightForWidth(tile_width)
				stack_occupancy[stack_ind] += 1
			else:
			# If the stack is full, proceed to the next one.
				stack_ind += 1
				stack_ind = stack_ind % n_tiles_across
				# Keep moving over stacks until we find a free one:
				while stack_heights[stack_ind] > avg_height:
					stack_ind += 1
				# Assign this child to that 
				stack[i] = stack_ind % n_tiles_across
				stack_heights[stack_ind] += tiles[i].heightForWidth(tile_width)
				stack_occupancy[stack_ind] += 1

			stack_ind += 1
			stack_ind = stack_ind % n_tiles_across

		# Equalize the stack heights with spacer elements:
		max_height = max(stack_heights)

		vboxlayouts = []

		for i in range(n_tiles_across):
			vboxlayout = QVBoxLayout()
			vboxlayouts.append(vboxlayout)
		for i, tile in enumerate(tiles):
			tile.column = stack[i]
			vboxlayouts[stack[i]].addWidget(tile)

		for i in range(n_tiles_across):
			vboxlayouts[i].addSpacing(max_height - stack_heights[i])
			source_columns.addLayout(vboxlayouts[i])

		self.source_columns.setContentsMargins(int(self.padding_x), 11,\
												int(self.padding_x), 11)
		self.source_grid_container.setLayout(source_columns)
		self.setWidget(self.source_grid_container)
		self..setAlignment(Qt.AlignHCenter)

	# Adjust the padding to adjust to a new available_width parameter:
	def adjust(self, available_width):
		available_width = available_width - 2 * self.padding_x

		available_width -= self.spacing_x * (self.n_tiles_across - 1)
		self.available_width = max(0, self.available_width)

		extra_padding = max(0, (self.available_width/self.n_tiles_across \
												- self.tile_width)/2)
		self.padding_x += extra_padding

		self.source_grid_container.setContentsMargins(int(self.padding_x), 11,\
													  int(self.padding_x), 11)
	# Redraw the 
	def redraw(self, available_width):

		self.available_width = available_width - 2 * self.padding_x

		# Remove the children of the horizontal box layout
		for i in reversed(range(self.source_columns.count())):
			self.source_columns.itemAt(i).widget().setParent(None)

		self.arrange_layout()

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
		self.app.content_area_widget.show()

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
