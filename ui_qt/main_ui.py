import sys
import os
from math import ceil, floor
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout, QMainWindow, QToolBar,
							 QSizePolicy, QGraphicsOpacityEffect, QDockWidget,
							 QTabWidget)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer

from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders
from pdf_viewer import PDFViewerContainer
from widgets import (DockWidget, TabWidget, SourceTile,
					Content_Area_Widget, SourceSelector,
					BackButton, SourceThumbnail)
from tile_layout import TileLayout
import pdb

active_sources = Spiders.spiders


class App(QMainWindow):

	# Since we begin at home, the active_source is None
	active_source = None

	# Begin with no pdf dock widget
	ntabs = 0

	# Dictionary of various geometry parameters. Fed into TileLayout
	global_geometry_params = {}

	# Source Page
	global_geometry_params["source_page"] = {}
	global_geometry_params["source_page"]["tile_spacing_x"] = 10
	# Sets the vertical spacing between tiles in source view
	global_geometry_params["source_page"]["tile_spacing_y"] = 10
	# Sets the margins within the scroll area in the source view
	global_geometry_params["source_page"]["tile_area_margin_x"] = 40
	global_geometry_params["source_page"]["tile_area_margin_y"] = 0

	# Ideally, how wide should the tiles be?
	global_geometry_params["source_page"]["target_dim"] = 400

	# This must be specified at the time of use depending on the current
	# width of the window's central widget. Right now it is set to None
	# because on initialization it has no meaning
	global_geometry_params["source_page"]["central_widget_width"] = None



	# At a Glance Section
	global_geometry_params["at_a_glance"] = {}
	# Sets the spacing between tile columns in new_articles
	global_geometry_params["at_a_glance"]["na_spacing_x"] = 10
	# Sets the vertical spacing between tiles in new_articles
	global_geometry_params["at_a_glance"]["na_spacing_y"] = 10
	# Sets the margins within the new_articles area in home view
	global_geometry_params["at_a_glance"]["na_area_margin_x"] = 40
	global_geometry_params["at_a_glance"]["na_area_margin_y"] = 0

	global_geometry_params["at_a_glance"]["target_dim"] = 400
	global_geometry_params["at_a_glance"]["central_widget_width"] = None


	# Source Selector Section
	global_geometry_params["source_selector"] = {}
	# Sets the spacing between tile columns in new_articles
	global_geometry_params["source_selector"]["source_spacing_x"] = 10
	# Sets the vertical spacing between tiles in new_articles
	global_geometry_params["source_selector"]["source_spacing_y"] = 10
	# Sets the margins within the new_articles area in home view
	global_geometry_params["source_selector"]["source_area_margin_x"] = 40
	global_geometry_params["source_selector"]["source_area_margin_y"] = 0
	global_geometry_params["source_selector"]["central_widget_width"] = None



	def __init__(self, parent=None):
		super(App, self).__init__(parent)

		self.load_data()

		self.init_window()

		self.init_startup_layout()

	# When the user resizes the window, if there are any docked pdfs
	# currently attached, update their size to keep track

	def resizeEvent(self, event):
		dock_widget = self.findChildren(QDockWidget)

		if dock_widget:

			width_fraction = dock_widget[0].width()/event.oldSize().width()

			self.resizeDocks(dock_widget, [self.width() * width_fraction], Qt.Horizontal)

			try:
				# Make room for the dock widget reisize
				target_geometry = QRect(self.centralWidget().geometry().x(), 
										self.centralWidget().geometry().y(),
										self.width() * (1 - width_fraction),
										self.centralWidget().height())
				self.content_area_widget.resize(target_geometry)
			except:
				pass
		elif self.centralWidget():

			# Otherwise change the size of the content area to 
			# match the window width
			target_geometry = QRect(self.centralWidget().geometry().x(), 
									self.centralWidget().geometry().y(),
									self.width(), self.centralWidget().height())
			self.content_area_widget.resize(target_geometry)
		else:
			pass

	# def adjust_source(self):
	# 	spacing_x = self.tile_spacing_x
	# 	padding_x = self.tile_area_margin_x

	# 	available_width = self.centralWidget().width() - 2 * padding_x
	# 	# Don't have to calculate n_tiles_across as it should not have changed
	# 	n_tiles_across = self.scroll_area.widget().layout().itemAt(0).count()
	# 	available_width -= spacing_x * (n_tiles_across - 1)
	# 	available_width = max(0, available_width)
	# 	# Tile width is always the target dim
	# 	tile_width = self.target_dim

	# 	# Add extra space to the margins
	# 	extra_padding = max(0, (available_width/n_tiles_across - tile_width)/2)
	# 	padding_x  += extra_padding

	# 	self.scroll_area.widget().layout().setContentsMargins(int(padding_x), 11, int(padding_x), 11)

	# def redraw_source(self):
	# 	# Remove exisiting scroll area widget
	# 	self.content_area.removeWidget(self.scroll_area)
	# 	self.scroll_area.setParent(None)
	# 	# Redraw with the new window size:
	# 	self.scroll_area = self.init_scrollarea(self.active_source)
	# 	# Add the scroll area back
	# 	self.content_area.addWidget(self.scroll_area)

	def load_data(self):
		self.data = {}
		for src in active_sources:
			self.data[src] = read_json.read_data(src)

	def init_window(self):
		
		self.setGeometry(100, 100,  800, 800)
		self.setWindowTitle("Ankit's Crawler")
		self.setDockOptions(QMainWindow.ForceTabbedDocks)
		self.setDockNestingEnabled(True)
		self.show()

	# Set certain widgets as attributes so that they can 
	# be easily referenced when needed
	def init_startup_layout(self):
		self.root_layout = QVBoxLayout()
		self.topmenu = self.init_topmenu()
		self.addToolBar(self.topmenu)

		self.content_area_widget = Content_Area_Widget(self)
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

		sources = TileLayout(self, self.global_geometry_params["source_selector"])
		sources.set_children(active_sources, SourceThumbnail)


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
				article_entry = SourceTile(data=new_articles_list[ind], app=self)
				new_articles_layout.addWidget(article_entry, i, j)

		new_articles.setLayout(new_articles_layout)
		new_articles.sizePolicy().setHorizontalPolicy(4)
		scroll_area.setWidget(new_articles)
		return scroll_area
	
	def animate_tile_layouts(self):

		# Find all the currently active tile layouts
		tile_layouts = self.content_area_widget.findChildren(TileLayout)

		for tile_layout in tile_layouts:
			for i, tile in enumerate(tile_layout.tiles):
				tile.initialize_animation()
				if i == len(tile_layout.tiles) - 1:
					tile.opacity_animation.finished.connect(tile_layout.reinsert_all_tiles)
				tile.delay.start(i * 25)


	# Set up a layout with a pressable button that will bring us back to the home page:
	def init_navigationbar(self):
		back_button = BackButton("Back",app=self)
		return back_button

	# Manage the PDF dockwidget:
	def add_pdf_dock(self, pdf_path):

		if self.ntabs == 0:
			# Create a new dock widget
			self.dockContainer = DockWidget(self)
			self.dockContainer.setAllowedAreas(Qt.RightDockWidgetArea)
			dock_tab_area = TabWidget(self)

			tab = PDFViewerContainer(pdf_path)
			label = "Tab %d"  % (self.ntabs + 1)
			dock_tab_area.addTab(tab, "Tab %d" % (self.ntabs + 1))

			self.ntabs += 1

			self.dockContainer.setWidget(dock_tab_area)

			self.addDockWidget(Qt.RightDockWidgetArea, self.dockContainer)

		else:
			# Add a tab to the existing tabwidget
			dock_tab_area = self.dockContainer.widget()

			tab = PDFViewerContainer(pdf_path)

			dock_tab_area.addTab(tab, "Tab %d" % (self.ntabs + 1))
			dock_tab_area.setCurrentWidget(tab)
			self.ntabs +=1 

		self.resizeDocks([self.dockContainer], [self.width()/2], Qt.Horizontal)
		try:
			target_geometry = QRect(self.centralWidget().geometry().x(), 
									self.centralWidget().geometry().y(),
									self.width()/2, self.centralWidget().height())
			self.content_area_widget.resize(target_geometry)
		except:
			pass

	# Switch to source page
	def switch_to_source(self, source):
		# Remove the home page widgets. Note this does note 
		# delete them so when we return_home they will be the same
		# unless they are explicitly adjusted somewhere else
		self.content_area.removeWidget(self.new_articles)
		self.new_articles.hide()
		self.content_area.removeWidget(self.sources)
		self.sources.hide()
		# Add the article view scroll area
		try:
			self.content_area.addWidget(self.navigation_bar)
			self.content_area.addWidget(self.scroll_area)
			self.animate_tile_layouts()
			self.navigation_bar.show()
			self.scroll_area.show()
		except:
			self.global_geometry_params["source_page"]["central_widget_width"] =\
			self.centralWidget().width()
			source_scroll_area = TileLayout(self,\
								self.global_geometry_params["source_page"])
			source_scroll_area.set_children(self.data[source], SourceTile)
			source_scroll_area.arrange_layout()
			self.scroll_area = source_scroll_area
			self.navigation_bar = self.init_navigationbar()

			self.content_area.addWidget(self.navigation_bar)
			self.content_area.addWidget(self.scroll_area)
			self.animate_tile_layouts()

		# When we switch for the first time, do the fade in
		# animation

		self.active_source = source

	# Return to home page
	def return_home(self):
		# Remove the source page widgets. Similar to switch_to_source
		# they are not deleted here
		self.content_area.removeWidget(self.navigation_bar)
		self.navigation_bar.hide()
		self.content_area.removeWidget(self.scroll_area)
		self.scroll_area.hide()
		try:
			self.content_area.addWidget(self.sources)
			self.content_area.addWidget(self.new_articles)
		except:
			self.sources = self.init_sourcs()
			self.new_articles = self.new_articles()
			self.content_area.addWidget(self.sources)
			self.content_area.addWidget(self.new_articles)

		self.sources.show()
		self.new_articles.show()

		self.active_source = None



if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())