import sys
import os
from math import ceil, floor
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout, QMainWindow, QToolBar,
							 QSizePolicy)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders
from PyQt5.QtCore import Qt
import pdb

active_sources = Spiders.spiders

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'


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
		super().__init__()

		tile_layout = QVBoxLayout()

		article = kwargs["article"]

		self.title = article["title"]
		self.authors = article["authors"]
		self.tags = article["tags"]
#		self.desc = article["desc"]
		self.desc = lorem_ipsum
		self.path = article["files"][0]["path"]


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



	def open_pdf(self):
		file_path = Paths.files_path + self.path
		os.startfile(file_path)


class App(QMainWindow):

	# Since we begin at home, the active_source is None
	active_source = None

	# Sets the spacing between tile columns in source view
	tile_spacing_x = 10
	# Sets the vertical spacing between tiles in source view
	tile_spacing_y = 10
	# Sets the margins within the scroll area in the source view
	tile_area_margin_x = 40
	tile_area_margin_y = 0

	# Ideally, how wide should the article tiles be?
	target_dim = 400

	# Sets the spacing between tile columns in new_articles
	na_spacing_x = 10
	# Sets the vertical spacing between tiles in new_articles
	na_spacing_y = 10
	# Sets the margins within the new_articles area in home view
	na_area_margin_x = 40
	na_area_margin_y = 0

	# Sets the spacing between tile columns in new_articles
	source_spacing_x = 10
	# Sets the vertical spacing between tiles in new_articles
	source_spacing_y = 10
	# Sets the margins within the new_articles area in home view
	source_area_margin_x = 40
	source_area_margin_y = 0


	def __init__(self):
		super().__init__()

		self.load_data()

		self.init_window()

		self.init_startup_layout()

	# When the user resizes the window, we check to see if
	# the content_area layout needs to be adjusted to 
	# fill space. 
	def resizeEvent(self, event):
		# If there is no central widget yet, then we do not need
		# to keep track fo resize
		if self.centralWidget():
			content_area_width = self.centralWidget().width()

			# At the moment, we only check for adjustment in the 
			# source view
			if self.active_source is None:
				return
			else:
				if content_area_width > self.max_width or\
					content_area_width < self.min_width:
					self.redraw_source()
				else:
					self.adjust_source()
	def adjust_source(self):
		spacing_x = self.tile_spacing_x
		padding_x = self.tile_area_margin_x

		available_width = self.centralWidget().width() - 2 * padding_x
		# Don't have to calculate n_tiles_across as it should not have changed
		columns = self.scroll_area.findChildren(QHBoxLayout)[0].findChildren(QVBoxLayout)

		n_tiles_across = len(columns)
		available_width -= spacing_x * (n_tiles_across - 1)
		tile_width = available_width/n_tiles_across

		for i in range(n_tiles_across):
			for j in range(columns[i].count()):
				try:
					columns[i].itemAt(j).widget().setFixedWidth(tile_width)
				except:
					continue



	def redraw_source(self):
		# Remove exisiting scroll area widget
		self.content_area.removeWidget(self.scroll_area)
		self.scroll_area.setParent(None)
		# Redraw with the new window size:
		self.scroll_area = self.init_scrollarea(self.active_source)
		# Add the scroll area back
		self.content_area.addWidget(self.scroll_area)

	def load_data(self):
		self.data = {}
		for src in active_sources:
			self.data[src] = read_json.read_data(src)

	def init_window(self):
		
		self.setGeometry(100, 100,  800, 800)
		self.setWindowTitle("Ankit's Crawler")
		self.show()

	# Set certain widgets as attributes so that they can 
	# be easily referenced when needed
	def init_startup_layout(self):
		self.root_layout = QVBoxLayout()
		self.topmenu = self.init_topmenu()
		self.addToolBar(self.topmenu)

		self.content_area_widget = QWidget()
		self.content_area = QVBoxLayout()

		self.sources = self.init_sources()
		self.new_articles = self.init_new_articles()

		self.content_area.addWidget(self.sources)
		self.content_area.addWidget(self.new_articles)

		self.content_area_widget.setLayout(self.content_area)
		self.setCentralWidget(self.content_area_widget)

	def init_topmenu(self):
		topmenu = QToolBar()
		Sync_Button = QPushButton("Sync")
		Last_Updated = QLabel("Last Updated:")
		topmenu.addWidget(Sync_Button)
		topmenu.addSeparator()
		topmenu.addWidget(Last_Updated)

		# Do not let the user drag the toolbar around
		topmenu.setMovable(False)
		return topmenu

	# List of sources
	def init_sources(self):
		sources = QGroupBox("Sources")
		sources_layout = QGridLayout()

		n_columns = 3
		n_rows = int(ceil(len(active_sources)/n_columns))

		for i in range(n_rows):
			for j in range(n_columns):
				ind = i * n_columns + j
				if ind >= len(active_sources):
					break
				label = SourceSelector(active_sources[ind], app=self,
															source=active_sources[ind])
				sources_layout.addWidget(label, i, j)

		sources.setLayout(sources_layout)
		return sources

	# Newest stories
	def init_new_articles(self):
		scroll_area = QScrollArea()
		scroll_area.setAttribute(Qt.WA_AcceptTouchEvents, on=True)

		new_articles = QGroupBox("At a Glance")
		new_articles_layout = QGridLayout()

		# Take the newest article from each source:
		new_articles_list = []
		for src in active_sources:
			if len(src) > 0:
				new_articles_list.append(self.data[src][0])

		n_columns = 3
		n_rows = int(ceil(len(new_articles_list)/n_columns))

		for i in range(n_rows):
			for j in range(n_columns):
				ind = i * n_columns + j
				if ind >= len(active_sources):
					break
				article_entry = SourceTile(article=new_articles_list[ind])
				new_articles_layout.addWidget(article_entry, i, j)

		new_articles.setLayout(new_articles_layout)
		new_articles.sizePolicy().setHorizontalPolicy(4)
		scroll_area.setWidget(new_articles)
		return scroll_area
    

	def init_scrollarea(self, source):
		# We can only proceed if the central widget has been initialized
		if self.centralWidget() is None:
			self.init_startup_layout()

		scroll_area = QScrollArea()
		# Enable touch screen functionality:
		scroll_area.setAttribute(Qt.WA_AcceptTouchEvents, on=True)

		source_grid_container = QWidget()
		# To achive a tile layout like functionality, we arrange vertical
		# box layouts in a horizontal box layout

		source_columns = QHBoxLayout()

		# Calculate the available width from the width and the margins.
		# This calculation is ported over from kivy TileLayout

		spacing_x = self.tile_spacing_x
		padding_x = self.tile_area_margin_x

		available_width = self.centralWidget().width() - 2 * padding_x


		n_tiles_across = max(1, int(floor((available_width + spacing_x)/
										(self.target_dim + spacing_x))))
		available_width -= spacing_x * (n_tiles_across - 1)

		# Tile width is always the target dim
		tile_width = self.target_dim
		# Add extra space to the margins
		padding_x  += (available_width/n_tiles_across - tile_width)/2

		# Assign a maximum and minimum width. If the window is resized outside
		# these bounds, then this method will be triggered and the layout will
		# be recalculated:

		# If the window is made wider than the width of an additional tile
		# plus the spacing, then redraw:
		self.max_width = available_width + self.target_dim + spacing_x

		# If the window is made smaller to the point that the tile_width would 
		# have to be reduced to below the target_dim, then redraw: 
		self.min_width = max(0, available_width -\
						(n_tiles_across * (tile_width - self.target_dim))) 

		# Assemble the children so that we can determine their heights:
		tiles = []
		total_height_needed = 0
		for article in self.data[source]:
			tile = SourceTile(article=article)
			tile.setFixedWidth(tile_width)
			total_height_needed += tile.heightForWidth(tile_width)
			tiles.append(tile)

		avg_height = float(total_height_needed)/n_tiles_across
		# Divide the children into stacks of equal height

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
			vboxlayouts[stack[i]].addWidget(tile)

		for i in range(n_tiles_across):
			vboxlayouts[i].addSpacing(max_height - stack_heights[i])
			source_columns.addLayout(vboxlayouts[i])

		source_columns.setContentsMargins(padding_x, 11, padding_x, 11)
		source_grid_container.setLayout(source_columns)
		scroll_area.setWidget(source_grid_container)

		return scroll_area

	# Set up a layout with a pressable button that will bring us back to the home page:
	def init_navigationbar(self):
		back_button = BackButton("Back",app=self)
		return back_button


	# Switch to source page
	def switch_to_source(self, source):
		# Remove the home page widgets
		self.content_area.removeWidget(self.new_articles)
		self.new_articles.setParent(None)
		self.content_area.removeWidget(self.sources)
		self.sources.setParent(None)
		# Add the article view scroll area
		try:
			self.content_area.addWidget(self.navigation_bar)
			self.content_area.addWidget(self.scroll_area)
		except:
			self.scroll_area = self.init_scrollarea(source)
			self.navigation_bar = self.init_navigationbar()
			self.content_area.addWidget(self.navigation_bar)
			self.content_area.addWidget(self.scroll_area)
		self.active_source = source

	# Return to home page
	def return_home(self):
		# Remove the source page widgets
		self.content_area.removeWidget(self.navigation_bar)
		self.navigation_bar.setParent(None)
		self.content_area.removeWidget(self.scroll_area)
		self.scroll_area.setParent(None)
		try:
			self.content_area.addWidget(self.sources)
			self.content_area.addWidget(self.new_articles)
		except:
			pdb.set_trace()
			self.sources = self.init_sourcs()
			self.new_articles = self.new_articles()
			self.content_area.addWidget(self.sources)
			self.content_area.addWidget(self.new_articles)

		self.active_source = None



if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())