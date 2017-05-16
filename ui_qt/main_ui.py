import sys
import os
from math import ceil
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout)
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

class SourceEntry(QVBoxLayout):

	def __init__(self, **kwargs):
		super().__init__()

		article = kwargs["article"]

		self.title = article["title"]
		self.authors = article["authors"]
		self.tags = article["tags"]
#		self.desc = article["desc"]
		self.desc = lorem_ipsum
		self.path = article["files"][0]["path"]

		self.addWidget(QLabel(self.title))
		secondary_text = "By %s" % self.authors
		secondary_text += "| "
		secondary_text += self.tags
		self.addWidget(QLabel(secondary_text))
		PDF_link = QPushButton("PDF")
		PDF_link.clicked.connect(self.open_pdf)
		self.addWidget(PDF_link)
		desc = QLabel(self.desc)
		desc.setWordWrap(True)
		self.addWidget(desc)

	def open_pdf(self):
		file_path = Paths.files_path + self.path
		os.startfile(file_path)


class App(QWidget):

	def __init__(self):
		super().__init__()

		self.load_data()

		self.init_window()

		self.init_root_layout()


	def load_data(self):
		self.data = {}
		for src in active_sources:
			self.data[src] = read_json.read_data(src)

	def init_window(self):
		
		self.setGeometry(100, 100,  800, 800)
		self.setWindowTitle("Helloz")
		self.show()

	# Set certain widgets as attributes so that they can 
	# be easily referenced when needed
	def init_root_layout(self):
		self.root_layout = QVBoxLayout()
		self.topmenu = self.init_topmenu()
		self.topmenu.setMaximumHeight(50)
		self.content_area = QVBoxLayout()

		self.sources = self.init_sources()

		self.new_articles = self.init_new_articles()

		self.content_area.addWidget(self.sources)
		self.content_area.addWidget(self.new_articles)

		self.root_layout.addWidget(self.topmenu)
		self.root_layout.addLayout(self.content_area)
		self.setLayout(self.root_layout)

	def init_topmenu(self):
		topmenu_widget = QWidget()
		topmenu = QHBoxLayout()
		Title = QLabel("Ankit's Crawler")
		Sync_Button = QPushButton("Sync")
		Last_Updated = QLabel("Last Updated:")
		topmenu.addWidget(Title)
		topmenu.addWidget(Sync_Button)
		topmenu.addWidget(Last_Updated)
		topmenu_widget.setLayout(topmenu)
		return topmenu_widget

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
				article_entry = SourceEntry(article=new_articles_list[ind])
				new_articles_layout.addLayout(article_entry, i, j)
		new_articles.setLayout(new_articles_layout)
		return new_articles
    


	def init_scrollarea(self, source):
		scroll_area = QScrollArea()

		# Enable touch screen functionality:
		scroll_area.setAttribute(Qt.WA_AcceptTouchEvents, on=True)
		source_grid_container = QWidget()

		source_grid = QGridLayout()

		for i in range(len(self.data[source])):
			source_grid.addLayout(SourceEntry(article=self.data[source][i]), i, 0)

		source_grid_container.setLayout(source_grid)
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




if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())