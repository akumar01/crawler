import sys
import os
from math import ceil, floor
from copy import copy
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout, QMainWindow, QToolBar,
							 QSizePolicy, QGraphicsOpacityEffect, QDockWidget,
							 QTabWidget, QDialog, QCheckBox)
from PyQt5.QtCore import QSize, QSequentialAnimationGroup, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer

from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders
from pdf_viewer import PDFViewerContainer
from widgets import (DockWidget, TabWidget, SourceTile,
					Content_Area_Widget, SourceSelector,
					BackButton, Thumbnail, SettingsDialog,
					initialize_animation)
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
	global_geometry_params["at_a_glance"]["tile_spacing_x"] = 10
	# Sets the vertical spacing between tiles in new_articles
	global_geometry_params["at_a_glance"]["tile_spacing_y"] = 10
	# Sets the margins within the new_articles area in home view
	global_geometry_params["at_a_glance"]["tile_area_margin_x"] = 40
	global_geometry_params["at_a_glance"]["tile_area_margin_y"] = 0

	global_geometry_params["at_a_glance"]["target_dim"] = 400
	global_geometry_params["at_a_glance"]["central_widget_width"] = None


	# Source Selector Section
	global_geometry_params["source_selector"] = {}
	# Sets the spacing between tile columns in new_articles
	global_geometry_params["source_selector"]["tile_spacing_x"] = 10
	# Sets the vertical spacing between tiles in new_articles
	global_geometry_params["source_selector"]["tile_spacing_y"] = 10
	# Sets the margins within the new_articles area in home view
	global_geometry_params["source_selector"]["tile_area_margin_x"] = 40
	global_geometry_params["source_selector"]["tile_area_margin_y"] = 0
	global_geometry_params["source_selector"]["central_widget_width"] = None


	global_geometry_params["source_selector"]["target_dim"] = 250
	# Source Selector Thumbnail Size
	global_geometry_params["source_selector"]["thumbnail"] = {}
	# Keep aspect ratio
	global_geometry_params["source_selector"]["thumbnail"]["maintain_aspect_ratio"] =\
	1
	# Shoot for 200 by 100 thumbnails
	global_geometry_params["source_selector"]["thumbnail"]["geometry_target"] =\
	[250, 125]


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
			self.data[src] = {}
			self.data[src]["entries"] = read_json.read_data(src)
			self.data[src]["thumbnail"] = '%s/source_thumbnails/%s.PNG'\
											% (Paths.ui_path, src)

	# When the sync button is clicked, actually perform the sync, and update the
	# view to incorporate any new articles found
	def do_sync(self):
		sync_button = self.topmenu.findChildren(QPushButton)[0]
		sync_button.setEnabled(False)
		sync_button.setText("Syncing...")
		# Performs the web crawl in a subprocess
		do_crawl()
		sync_button.setText("Sync")
		sync_button.setEnabled(True)
		self.update_views()

	# Redraw all views on the data
	def update_views(self):
		# Re-read all the JSON files
		self.data = self.load_data()

		# If we're on the home page, need to 
		# update new_articles and sources
		if self.source is None:

			# Take the newest article from each source:
			new_articles_list = []

			# Source Thumbnails
			children = []

			for i, src in enumerate(active_sources):
				children.append(copy(geometry_params))
				children[i]["image"] = self.data[src]["thumbnail"]
				children[i]["source"] = src
				if len(src) > 0:
					new_articles_list.append(self.data[src]["entries"][0])

				self.new_articles.update_children(new_articles_list)
				self.sources.update_children(children)
		# Update the children of the scroll_area
		else:

			self.scroll_area.update_children(self.data)



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

		# Need to add the content_area_widget to the main window 
		# before initializing its contents so we have information 
		# about widths
		self.content_area_widget.setLayout(self.content_area)
		self.setCentralWidget(self.content_area_widget)


		self.sources = self.init_sources()
		self.new_articles = self.init_new_articles()

		self.content_area.addWidget(self.sources)
		self.content_area.addWidget(self.new_articles)

	def popup_settings(self):
		settings = self.load_settings()
		settings_dialog = SettingsDialog(app=self)
		settings_dialog.exec_()


	def init_topmenu(self):
		topmenu = QToolBar()
		Sync_Button = QPushButton("Sync")
		Sync_Button.clicked.connect(self.do_sync)
		Last_Updated = QLabel("Last Updated:")
		settings = QPushButton("Settings")
		settings.clicked.connect(self.popup_settings)
		topmenu.addWidget(Sync_Button)
		topmenu.addSeparator()
		topmenu.addWidget(Last_Updated)	
		topmenu.addWidget(settings)
		# Do not let the user drag the toolbar around
		topmenu.setMovable(False)
		return topmenu

	# List of sources
	def init_sources(self):

#		sources = QGroupBox("Sources")

		children = []
		geometry_params = self.global_geometry_params["source_selector"]["thumbnail"]
		for i, src in enumerate(active_sources):
			children.append(copy(geometry_params))
			children[i]["image"] = self.data[src]["thumbnail"]
			children[i]["source"] = src

		self.global_geometry_params["source_selector"]["central_widget_width"] =\
		self.content_area_widget.width()

		source_tile_layout = TileLayout(self, self.global_geometry_params["source_selector"])
		source_tile_layout.set_children(children, Thumbnail)
		source_tile_layout.arrange_layout()
#		source_layout = QVBoxLayout()
#		source_layout.addWidget(source_tile_layout)
#		sources.setLayout(source_layout)
		return source_tile_layout

	# Newest stories
	def init_new_articles(self):

		geometry_params = self.global_geometry_params["at_a_glance"]
		geometry_params["central_widget_width"] = self.content_area_widget.width()
		new_articles = TileLayout(self, geometry_params)

		# Take the newest article from each source:
		new_articles_list = []
		for src in active_sources:
			if len(src) > 0:
				new_articles_list.append(self.data[src]["entries"][0])

		new_articles.set_children(new_articles_list, SourceTile)
		new_articles.arrange_layout()

		return new_articles
	


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
		# unless they are explicitly  somewhere else
		self.content_area.removeWidget(self.new_articles)
		self.new_articles.hide()
		self.content_area.removeWidget(self.sources)
		self.sources.hide()

		# Add the article view scroll area. 

		self.global_geometry_params["source_page"]["central_widget_width"] =\
		self.centralWidget().width()
		source_scroll_area = TileLayout(self,\
							self.global_geometry_params["source_page"])
		source_scroll_area.set_children(self.data[source]["entries"], SourceTile)
		source_scroll_area.arrange_layout()
		self.scroll_area = source_scroll_area

		if ~hasattr(self, 'navigation_bar'):
			self.navigation_bar = self.init_navigationbar()

		self.content_area.addWidget(self.navigation_bar)
		self.content_area.addWidget(self.scroll_area)

		self.scroll_area.animate_tiles()

		# When we switch for the first time, do the fade in
		# animation

		self.active_source = source

	# Return to home page
	def return_home(self):
		# Remove the source page widgets. Unlike switch_to_source,
		# we delete the scroll area because it is likely that we 
		# will switch to a difference source next time, in which 
		# case it has to be re-initialized anyways

		self.content_area.removeWidget(self.navigation_bar)
		self.navigation_bar.hide()
		self.content_area.removeWidget(self.scroll_area)
		self.scroll_area.hide()

		if ~hasattr(self, 'sources'):
			self.sources = self.init_sources()
		if ~hasattr(self, 'new_articles'):
			self.new_articles = self.init_new_articles()
	
		self.content_area.addWidget(self.sources)
		self.content_area.addWidget(self.new_articles)

		self.sources.show()
		self.new_articles.show()

		self.sources.animate_tiles()
		self.new_articles.animate_tiles()


		self.active_source = None



if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())