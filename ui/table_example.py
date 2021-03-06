from kivy.config import Config
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import json_lines
from crawler.agg.json_out import read_json
from crawler.project_vars import Paths, Spiders, settings_master_list
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from scrapy.crawler import Crawler
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from custom_crawler import CustomCrawler
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy import signals
from crawler.agg.spiders.nature_spider import NatureSpider
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock, mainthread
import threading
import logging
import pdb
import time 
import os
import sys
from math import ceil
from crawler.crawl_test import do_crawl, read_sync_settings
from kivy.core.window import Window
from kivy.uix.settings import SettingsWithTabbedPanel, SettingTitle, SettingsPanel, SettingBoolean, SettingNumeric
from dynamicboxlayout import DynamicBoxLayout
from tilelayout import TileLayout

active_sources = Spiders.spiders

# This JSON defines entries we want to appear in our App configuration screen
json = '''
[{
	"type": "options",
	"title": "Active Spiders",
	"desc": "Choose which spiders to actively sync",
	"section": "Sync Settings",
	"key": "active_spiders",
	"options": ["nature_news"]
}]
'''

class ArticleView(ModalView):
	def __init__(self, **kwargs):
		super(ArticleView, self).__init__(**kwargs)
	   # self.add_widget(CefBrowser(start_url = r"C:\Users\Ankit\Documents\crawler_project\crawler\agg\files\nature_news\2d0756ddeb451073a8097af3a009194160cfd58d.pdf"))
	   # self.add_widget(CefBrowser(start_url = r"C:\Users\Ankit\Documents\crawler_project\crawler\agg\nature-news-archive.html"))
#        c = CefBrowser()
#        self.add_widget(c)
#        c.change_url(r'https://ecee.colorado.edu/~ecen5345/Resources/Maznev14_Umklapp.pdf')
class TableHeader(Label):
	pass


class TableItem(Label):
	pass

class ArticleLink(Label):
	pass

class ArticleEntry(DynamicBoxLayout):
	title = StringProperty()
	authors = StringProperty()
	file_path = StringProperty()
	thumbnail_path = StringProperty()

	def __init__(self, **kwargs):
		super(ArticleEntry, self).__init__(**kwargs)
		self.title = kwargs['title']
		self.authors = kwargs['authors']
		self.file_path = kwargs['file_path']
		self.thumbnail_path = Paths.root_path + '/agg/thumbnail.jpg'
#        self.thumbnail_path = 'C:\\Users\\Ankit\\Documents\\crawler_project\\crawler\\agg\\thumbnail.jpg'

	# Add a shadow to the box to make it pop out.
	def add_shadow(self):
		# Wait until the widget is properly initiated in the widget
		# tree
		if(self.parent):
			shadow = InstructionGroup()
			# Need to tie dimensions of 
			spacing = self.parent.spacing
			# vertical shadow
			shadow.add(Color(0.25, 0.25, 0.25, 0.25))
			shadow.add(Rectangle(size=(0.1 * spacing[0], self.height), 
				pos=(self.x + self.width, self.y - 0.1 * spacing[1])))
			shadow.add(Rectangle(size=(0.98 * self.width, spacing[1]),
								 pos=(self.x +  spacing[0], self.y - 0.1 * spacing[1])))
			self.canvas.add(shadow)



	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			pass
			#os.startfile(self.file_path)
			#m = ArticleView()
			#m.view()


class SourceHeader(Label):

	def __init__(self, **kwargs):
		super(SourceHeader, self).__init__(**kwargs)
		self.text = kwargs['src']

class SourceContainer(GridLayout):
	src = StringProperty()

	def __init__(self, **kwargs):
		super(SourceContainer, self).__init__(**kwargs)
		self.add_widget(SourceHeader(src = self.src))
		self.add_widget(ArticleTable(src = self.src, id = 'table'))

# class SourceBoxes(GridLayout):
#     def __init__(self, **kwargs):
#         super(SourceBoxes, self).__init__(**kwargs)
#         for src in active_sources:
#             self.add_widget(SourceContainer(src = src, id = src))

class ScrollContainer(ScrollView):

	def __init__(self, **kwargs):
		super(ScrollContainer, self).__init__(**kwargs)
		self.src = kwargs["src"]
		self.add_widget(SourceContainer(src = self.src))

class ArticleCarouselContainer(GridLayout):
	def __init__(self, **kwargs):
		super(ArticleCarouselContainer, self).__init__(**kwargs)
		c = Carousel(direction="right")
		for src in active_sources:
			c.add_widget(ScrollContainer(src = src))
		f = BoxLayout(size_hint = (1, 0.1))
		b1 = Button(text = 'previous source')
		f.add_widget(b1)
		b2 = Button(text = 'next source')
		f.add_widget(b2)
		self.add_widget(f)
		self.add_widget(c)

		b1.bind(on_press= lambda x: c.load_previous())
		b2.bind(on_press = lambda x: c.load_next())



class ArticleTable(TileLayout):
	update_count = NumericProperty()

	def __init__(self, **kwargs):
		super(ArticleTable, self).__init__(**kwargs)
		self.src = kwargs['src']
		self.fetch_data()
		self.display_data(self.data)

	def on_update_count(self, *args):
		old_items = self.data
		self.fetch_data()
		new_items = [x for x in self.data if x not in old_items]
		self.display_data(new_items)

	def fetch_data(self):
		self.data = read_json.read_data(self.src)
	def display_data(self, data):

		# Data is always displayed in two columns. Divide the data in
		# half, rounding up for the first column
		# data_1 = data[:int(ceil(float(len(data))/2))]
		# data_2 = data[int(ceil(float(len(data))/2)):]

		# c1 = DynamicBoxLayout(orientation = 'vertical', size_hint_y = None,
		#                       height = self.minimum_height)
		# c2 = DynamicBoxLayout(orientation = 'vertical', size_hint_y = None,
		#                       height = self.minimum_height)

		# for entry in data_1:
		#     c1.add_widget(self.create_rows(entry))
		# for entry in data_2:
		#     c2.add_widget(self.create_rows(entry))


		# self.add_widget(c1)
		# self.add_widget(c2)


		for entry in data:
			child = self.create_rows(entry)
			self.add_widget(child)
			# Can't add shadow to the article tiles until 
			# they are added to the table because they depend 
			# on the table spacing
			child.add_shadow()


	def empty_message(self):
		return Label(text = 'Nothing to see here. Try syncing.')

	# def create_header(self, i):
	#     first_column = TableHeader(text='Title')
	#     second_column = TableHeader(text='Author(s)') 
	#     third_column = TableHeader(text='Tags')
	#     fourth_column = TableHeader(text='Link')
	#     return [first_column, second_column, third_column, fourth_column]

	# def create_header(self, src):
	#     src_thumbnail = Image(source = 'crawler/agg/media/src_thumbnails/nature_news.png')
	#     src_name = HeaderLabel(text = src)

	# def create_rows(self, data, i):
	#     first_column = TableItem(text=data[i]['title'])
	#     authors = ''
	#     if(len(data[i]["authors"]) > 1):
	#         authors += data[i]["authors"][0]
	#         for author in data[i]["authors"][1:]:
	#             authors += ", %s" % author
	#     elif(len(data[i]["authors"]) == 1):
	#         authors = data[i]["authors"][0]
	#     second_column = TableItem(text=authors)
	#     third_column = TableItem(text=data[i]['tags'])
	#     fourth_column = TableItem(text='PDF')
	#     return [first_column, second_column, third_column, fourth_column]

	def create_rows(self, data_entry):
		authors = ''
		if(len(data_entry["authors"]) > 1):
			authors += data_entry["authors"][0]
			for author in data_entry["authors"][1:]:
				authors += ", %s" % author
		elif(len(data_entry["authors"]) == 1):
			authors = data_entry["authors"][0]
		file_path = Paths.files_path + data_entry["files"][0]["path"]
		return ArticleEntry(title = data_entry['title'], authors = authors,\
							file_path = file_path, size_hint_y= None)        

class TopRow(Widget):
	def __init__(self, **kwargs):
		super(TopRow, self).__init__(**kwargs)
	def schedule_sync(self):
		t = threading.Thread(target = self.do_sync)
		t.start()

	def do_sync(self):
		self.start_sync()
#        Clock.schedule_once(self.start_sync)
		do_crawl()
#        Clock.schedule_once(self.finish_sync)
		self.finish_sync()

	@mainthread
	def start_sync(self, *args):
		self.ids.sync_button.disabled = True
		self.ids.sync_button.text = 'Syncing...'

	@mainthread
	def finish_sync(self, *args):
		pdb.set_trace()
		for src_box in root.ids.bottom_row.ids.src_box.children:
			src_box.children[0].update_count += 1
		self.ids.sync_button.disabled = False
		self.ids.sync_button.text = 'Sync'

class RootGrid(GridLayout):
	def __init__(self, **kwargs):
		super(RootGrid, self).__init__(**kwargs)
		self.rows = 2

class TestApp(App):

	def build(self):
		# Allow the root widget, RootGrid, to be globally accessible in python
		global root
		root = self.root
		self.settings_cls = SettingsWithTabbedPanel 


	def build_config(self, config):
		"""
		Set the default values for the configs sections.
		"""

		# Load the saved config files

#        config.update_config('test.ini', overwrite=True)
#        config.setdefaults('Sync Settings', {'booleantest': '0', 'font_size': 20})
		settings = read_sync_settings() 

		# It may be possible that since the last time the config file was saved, the 
		# configurable settings and list of selectable spiders has changed. Compare 
		# against the master list of settings, and then override with changes from the config
		# file

		settings_master = settings_master_list()
		default_settings = {}
		for setting in settings_master.keys():
			if setting in settings.keys():
				default_settings[setting] = settings[setting]
			else:
				default_settings[setting] = settings_master[setting][1]
		config.setdefaults('Sync Settings', default_settings)

	def build_settings(self, settings):
		"""
		Add our custom section to the default configuration object.
		"""
		# We use the string defined above for our JSON, but it could also b
		# loaded from a file as follows:
		#     settings.add_json_panel('My Label', self.config, 'settings.json')
#        settings.add_json_panel('My Label', self.config, data=json)
		title = 'Sync Settings'
		settings_list = settings_master_list()
		panel = SettingsPanel(title=title, settings= settings, config = self.config)
 
		for setting in settings_list.keys():
			if settings_list[setting][0] == 'boolean':
				s = SettingBoolean(panel = panel, title = setting, section="Sync Settings",
								key = setting)
			elif settings_list[setting][0] == 'numeric':
				s = SettingNumeric(panel = panel, title = setting, section = "Sync Settings",
									key = setting)
			panel.add_widget(s)
#        panel.add_widget(SettingTitle(text = 'Active Spiders'))
		uid = panel.uid
		if settings.interface is not None:
			settings.interface.add_panel(panel, title , uid)
		# Create a list of boolean settings to allow us to select which spiders to
		# actively crawl on sync




	def on_config_change(self, config, section, key, value):
		"""
		Respond to changes in the configuration.
		"""
#       Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
#            config, section, key, value))

		pass

	def close_settings(self, settings=None):
		"""
		The settings panel has been closed.
		"""
#        Logger.info("main.py: App.close_settings: {0}".format(settings))
		super(TestApp, self).close_settings(settings)
		self.config.write()

if __name__  == "__main__":
	TestApp().run()
