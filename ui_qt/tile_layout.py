import pdb
from math import floor
import numpy as np
from PyQt5.QtWidgets import (QWidget, QDockWidget, QTabWidget, QLabel,
							QPushButton, QHBoxLayout, QVBoxLayout,
							QGraphicsOpacityEffect, QSizePolicy,
							QToolBar, QScrollArea)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from crawler.project_vars import Paths, Spiders

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


class TileLayout(QScrollArea):

	def __init__(self, app, geometry_params):
		super(TileLayout, self).__init__()
		self.app = app
		self.geometry_params = geometry_params

		self.init()
		self.init_geometry(geometry_params)
		self.setWidgetResizable(True)

	def init(self):

		# Container widget
		self.source_grid_container = QWidget()

		# To achive a tile layout like functionality, we arrange vertical
		# box layouts in a horizontal box layout

		self.source_columns = QHBoxLayout()											
		self.source_grid_container.setAttribute(Qt.WA_AcceptTouchEvents, on = True)


	# Setup basic layout parameters
	def init_geometry(self, geometry_params):

		# Calculate the available width from the width and the margins.
		# This calculation is ported over from kivy TileLayout

		self.spacing_x = geometry_params["tile_spacing_x"]
		self.padding_x = geometry_params["tile_area_margin_x"]

		# Tile width is always the target dim
		self.tile_width = geometry_params["target_dim"]
		self.available_width = geometry_params["central_widget_width"] -\
							2 * self.padding_x

		self.n_tiles_across =  max(1, int(floor((self.available_width\
				 + self.spacing_x)/(self.tile_width + self.spacing_x))))

		# Add extra space to the margins
		self.padding_x += (self.available_width/self.n_tiles_across\
												 - 	self.tile_width)/2

		# Sets the maximum width that the layout can be expanded before
		# we would have enough room to add an additional column across
		self.max_width = self.available_width + self.tile_width \
											  + self.spacing_x

		# Sets the minimum width that the layout can be contracted in width
		# before we would have room for one fewer column across. If there is 
		# currently only one column, then the min_width is set to 0 (i.e. we
		# let a horizontal scroll bar appear)
		self.min_width = max(0, self.available_width - self.tile_width \
													 - self.spacing_x) 


	# Assign information necessary to create children to the TileLayout
	# children_cls determines which class to make the children out of 
	def set_children(self, children, children_cls):

		self.tiles = []
		self.total_height_needed = 0
		self.cls = children_cls
		for child in children:
			tile = children_cls(data = child, app = self.app)
			tile.setFixedWidth(self.tile_width)
			# Use height if the tile is a widget, heightForWidth if the
			# the tile is a layout. In the case that we use height, it is
			# a good idea to make sure that the widget is already scaled to
			# the right width, and that it matches self.tile_width
			if tile.heightForWidth(self.tile_width) > 0:
				self.total_height_needed += tile.heightForWidth(self.tile_width)
			else:
				self.total_height_needed += tile.height()
			self.tiles.append(tile)

	# Update the children, keeping track of differences between new and old children/
	def update_children(self, new_children):

		old_children = self.tiles
		self.tiles = []
		for child in new_children:
			tile = self.cls(data = child, app = self.app)
			tile.setFixedWidth(self.tile_width)
			if tile.heightForWidth(self.tile_width) > 0:
				self.total_height_needed += tile.heightForWidth(self.tile_width)
			else:
				self.total_height_needed += tile.height()
			self.tiles.append(tile)

		# Compare differences between old and new tiles
		diff_children = np.setdiff1d(self.tiles, old_children)

		# Do something with this difference:

		# Need to re-arrange the layout:
		self.arrange_layout()

	# Call after children have been correctly assigned to actually sort them 
	# into the appropriate columns
	def arrange_layout(self):

		self.avg_height = float(self.total_height_needed)/self.n_tiles_across
		self.n_tiles_across = min(self.n_tiles_across, len(self.tiles))
		tiles = self.tiles
		n_tiles_across = self.n_tiles_across
		avg_height = self.avg_height
		tile_width = self.tile_width
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
				if tiles[i].heightForWidth(tile_width) > 0:	
					stack_heights[stack_ind] += tiles[i].heightForWidth(tile_width)
				else:
					stack_heights[stack_ind] += tiles[i].height()
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
				if tiles[i].heightForWidth(tile_width) > 0:
					stack_heights[stack_ind] += tiles[i].heightForWidth(tile_width)
				else:
					stack_heights[stack_ind] += tiles[i].height()
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
			self.source_columns.addLayout(vboxlayouts[i])

		self.source_columns.setContentsMargins(int(self.padding_x), 11,\
		 										int(self.padding_x), 11)
		
		if self.source_grid_container.layout() != self.source_columns:
			self.source_grid_container.setLayout(self.source_columns)

		if self.widget() != self.source_grid_container:
			self.setWidget(self.source_grid_container)

		self.setAlignment(Qt.AlignHCenter)

	# Adjust the padding to adjust to a new available_width parameter:
	def adjust(self, available_width):
		# old_available_width = self.available_width
		# self.available_width = available_width - 2 * self.padding_x
		# self.available_width = max(0, self.available_width)

		# padding_delta = self.available_width - old_available_width

		# # extra_padding = max(0, (self.available_width/self.n_tiles_across \
		# # 										- self.tile_width)/2)
		# self.padding_x += padding_delta
		# self.padding_x = max(0, self.padding_x)
		pass
#		self.source_columns.setContentsMargins(int(self.padding_x), 11,\
#											   int(self.padding_x), 11)\

	# Redraw the tile layout on the basis of new available width (call on resize)
	def redraw(self, available_width):
		self.geometry_params["central_widget_width"] = available_width

		self.init()

		self.init_geometry(self.geometry_params)

		self.arrange_layout()

	# Need to do this to avoid strange rendering issues after fade in animation
	def reinsert_all_tiles(self):

		n_tiles_across = self.n_tiles_across

		for i in range(n_tiles_across):
			parent = self.source_columns.itemAt(i)
			n_rows = parent.count()
			for j in range(n_rows):
				child = parent.itemAt(j).widget()
				if child:
					parent.removeWidget(child)
					child.setParent(None)
					parent.insertWidget(j, child)
#	Define an animation to apply to all tiles
	def animate_tiles(self):

		for i, tile in enumerate(self.tiles):
			initialize_animation(tile)
			if i == len(self.tiles) - 1:
				tile.opacity_animation.finished.connect(self.reinsert_all_tiles)
			tile.delay.start(i * 25)


