import sys
import os
from math import ceil
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout,
							 QGroupBox, QStackedLayout)
from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders
import pdb

active_sources = Spiders.spiders

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'


class SourceSelector(QLabel):

	def __init__(self, **kwargs):
		super().__init__()

	def mouse_proess(self):
		pass


class SourceEntry(QVBoxLayout):

	def __init__(self, **kwargs):
		super().__init__()

		self.title = kwargs["title"]
		self.authors = kwargs["authors"]
		self.tags = kwargs["tags"]
		self.desc = kwargs["desc"]
		self.path = kwargs["file_url"]

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
			self.data["src"] = read_json.read_data(src)

	def init_window(self):
		
		self.setGeometry(100, 100,  800, 800)
		self.setWindowTitle("Helloz")
		self.show()

	def init_root_layout(self):
		root_layout = QVBoxLayout()
		topmenu = self.init_topmenu()

		content_area = QVBoxLayout()

		sources = self.init_sources()

		new_articles = self.init_new_articles()

		content_area.addWidget(sources)
		content_area.addWidget(scroll_area)

		root_layout.addLayout(topmenu)
		root_layout.addLayout(content_area)
		self.setLayout(root_layout)

	def init_topmenu(self):
		topmenu = QHBoxLayout()
		Title = QLabel("Ankit's Crawler")
		Sync_Button = QPushButton("Sync")
		Last_Updated = QLabel("Last Updated:")
		topmenu.addWidget(Title)
		topmenu.addWidget(Sync_Button)
		topmenu.addWidget(Last_Updated)
		return topmenu

	# List of sources
	def init_sources(self):
		sources = QGroupBox("Sources")
		sources_layout = QGridLayout()

		n_columns = 3
		n_rows = int(ceil(len(active_sources)/n_columns.))

		for i in range(n_rows):
			for j in range(n_columns):
				ind = i * n_columns + j
				if ind >= len(active_sources):
					break
				label = QLabel(active_sources[ind])
				sources_layout.addWidge(label)

		sources.setLayout(sources_layout)
		return sources

	# Newest stories
	def init_new_articles(self):
		new_articles = QGroupBox("At a Glance")
		new_articles_layout = QGridLayout()

		# Take the newest article from each source:
		new_articles = []
		for src in active_sources:
			news_articles.append(self.data["src"][0])

		n_columns = 3
		n_rows


	def init_scrollarea(self):
		source_stack = QStackedLayout()

		for source in active_sources:

			scroll_area = QScrollArea()

			source_grid = QGridLayout()

			for i in range(len(data)):
				source_grid.addLayout(SourceEntry(title=data[i]["title"],
												  authors=data[i]["authors"],
												  tags=data[i]["tags"],
												  desc=lorem_ipsum, 
												  file_url=data[i]["files"][0]["path"]), i, 0)


			scroll_area.setLayout(source_grid)
			source_stack.addWidget(scroll_area)
		return scroll_area


if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())