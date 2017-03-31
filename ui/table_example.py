from kivy.config import Config
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import json_lines
from crawler.agg.json import read_json
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from scrapy.crawler import Crawler
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from custom_crawler import CustomCrawler
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy import signals
from crawler.agg.spiders.nature_spider import NatureSpider
from kivy.clock import Clock, mainthread
import threading
import logging
import pdb
import time 
import os
import sys
from crawler.crawl_test import do_crawl

class TableHeader(Label):
    pass


class TableItem(Label):
    pass

class ScrollContainer(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollContainer, self).__init__(**kwargs)
        self.article_table = ObjectProperty(None)

class ArticleTable(GridLayout):
    update_count = NumericProperty()

    def __init__(self, **kwargs):
        super(ArticleTable, self).__init__(**kwargs)
        self.fetch_data()
        self.display_data(self.data)

    def on_update_count(self, *args):
        old_items = self.data
        self.fetch_data()
        new_items = [x for x in self.data if x not in old_items]
        self.display_data(new_items, 0)

    def fetch_data(self):
        self.data = read_json.read_data('nature_news')
    def display_data(self, data, create_header = 1):
        for i in xrange(len(data)):
            if i < 1 and create_header:
                row = self.create_header(i)
            else:
                row = self.create_rows(data, i)
            for item in row:
                self.add_widget(item)

    def create_header(self, i):
        first_column = TableHeader(text='Title')
        second_column = TableHeader(text='Author(s)') 
        third_column = TableHeader(text='Tags')
        fourth_column = TableHeader(text='Link')
        return [first_column, second_column, third_column, fourth_column]

    def create_rows(self, data, i):
        first_column = TableItem(text=data[i]['title'])
        authors = ''
        if(len(data[i]["authors"]) > 1):
            authors += data[i]["authors"][0]
            for author in data[i]["authors"][1:]:
                authors += ", %s" % author
        elif(len(data[i]["authors"]) == 1):
            authors = data[i]["authors"][0]
        second_column = TableItem(text=authors)
        third_column = TableItem(text=data[i]['tags'])
        fourth_column = TableItem(text='PDF')
        return [first_column, second_column, third_column, fourth_column]

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
        root.bottom_row.scroll_view.article_table.update_count += 1
        self.ids.sync_button.disabled = False
        self.ids.sync_button.text = 'Sync'

class AnchorContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(AnchorContainer, self).__init__(**kwargs)
        self.scroll_view = ObjectProperty(None)
class RootGrid(GridLayout):
    def __init__(self, **kwargs):
        super(RootGrid, self).__init__(**kwargs)
        self.rows = 2
        self.top_row = ObjectProperty(None)
        self.bottom_row = ObjectProperty(None)
class TestApp(App):
    def build(self):
        # Allow the root widget, RootGrid, to be globally accessible in python
        global root
        root = self.root

if __name__  == "__main__":
    TestApp().run()
