import sys
import os
from win32api import GetSystemMetrics
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QWidget,
							 QLabel, QPushButton, QScrollArea, QGridLayout)
from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders
import pdb

lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed interdum tempor tortor, vitae molestie lorem mattis et. Mauris consectetur massa non metus blandit scelerisque vestibulum nec augue. Donec eu venenatis dui. Praesent consectetur facilisis justo, quis porta odio convallis sit amet. Praesent congue quam eros, malesuada feugiat velit lacinia sit amet. Integer condimentum in nibh consectetur accumsan. Aliquam erat volutpat. Morbi eget vulputate dolor, quis malesuada nisl. Ut quis tincidunt purus, quis cursus augue. Vivamus vitae pellentesque elit, a sagittis nulla. Praesent varius, magna sit amet blandit porttitor, leo mauris sodales risus, varius vehicula quam elit vitae odio.'

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
		PDF_link.clicked.connect(self.open_pdf())
		self.addWidget(PDF_link)
		pdb.set_trace()
		desc = QLabel(self.desc)
		desc.setWordWrap(True)
		self.addWidget(desc)

	def open_pdf(self):
		file_path = Paths.files_path + self.path
		os.startfile(file_path)


class App(QWidget):

	def __init__(self):
		super().__init__()

		self.init_window()

		self.init_root_layout()


	def init_window(self):
		
		self.setGeometry(100, 100,  800, 800)
		self.setWindowTitle("Helloz")
		self.show()

	def init_root_layout(self):
		root_layout = QVBoxLayout()
		topmenu = self.init_topmenu()
		scroll_area = self.init_scrollarea()
		root_layout.addLayout(topmenu)
		root_layout.addWidget(scroll_area)
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

	def init_scrollarea(self):
		scroll_area = QScrollArea()
		source_container = QWidget()
		source_grid = QGridLayout()

		data = read_json.read_data('nature_news')

		for i in range(len(data)):
			source_grid.addLayout(SourceEntry(title=data[i]["title"],
											  authors=data[i]["authors"],
											  tags=data[i]["tags"],
											  desc=lorem_ipsum, 
											  file_url=data[i]["files"][0]["path"]), i, 0)
		source_container.setLayout(source_grid)
		scroll_area.setWidget(source_container)
		return scroll_area


if __name__ == "__main__":

	app = QApplication(sys.argv)
	root_widget = App()
	sys.exit(app.exec_())