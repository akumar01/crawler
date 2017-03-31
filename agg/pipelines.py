# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import os
import hashlib
import datetime
import scrapy
import logging
from scrapy.pipelines.files import FilesPipeline
from scrapy.exporters import JsonLinesItemExporter
from agg.items import JournalArticle

class AggPipeline(object):
    def process_item(self, item, spider):
        # Strip item fields of leading and trailing blank space:
        item = self.clean_spaces(item, spider)
        # Move downloaded files to appropriate directory and rename them:
        item = self.move_files(item, spider)
        
        # Make sure if any of title, tags, or author is empty, set it to a blank string
        if(not item["title"]):
            item["title"] = ""
        if(not item["authors"]):
            item["authors"] = ""
        if(not item["tags"]):
            item["tags"] = ""
        return item

    def clean_spaces(self, item, spider):
        # use isinstance(..., basestring) to check if the value is a string
        for key in item.keys():
            if(isinstance(item[key], basestring)):
                item[key] = item[key].strip()
        return item 

    def move_files(self, item, spider):
        # First, make sure that the directory we wish to move the files to exists. 
        # If not, we have to create it:
        f = 0;
        for file in item["files"]:
            filename = file["path"].split("/")[1]

            if(not os.path.exists("files")):
                os.makedirs("files")

            if(not os.path.exists("files/%s" % spider.name)):
                os.makedirs("files/%s" % spider.name)

            if(not os.path.exists('files/%s/%s' % (spider.name, filename))):
                os.rename("files/%s" % file["path"], "files/%s/%s" %\
                                (spider.name, filename))
            # Set the item file path to the new location and name
            item["files"][f]["path"] = "%s/%s" % (spider.name, filename)
            f+=1
        return item
# Extend the filespipeline so that we do not re-download files that have been already
# been downloaded.
class DownloadPDFS(FilesPipeline):
    def get_media_requests(self, item, info):
        for file_url in item["file_urls"]:            
            # Downloaded files are stored with hash filenames by default
            filename = hashlib.sha1(file_url).hexdigest()
            if(not os.path.exists("files/%s/%s.pdf" % (item["spider"], filename))):
                yield scrapy.Request(file_url)
            else: 
                logging.log(logging.INFO, 'File already exists!')

# Used for exporting items to json
class JsonPipeline(object):
    def open_spider(self, spider):

        # Initialize the directories where the jsonlines file is to be saved:
        if(not os.path.exists("json")):
            os.makedirs("json")

        if(not os.path.exists("json/%s" % spider.name)):
            os.makedirs("json/%s" % spider.name)

        # Make the JSONlines filename the datetime up to the minute
        filename = datetime.datetime.utcnow().strftime("%y_%b_%d_%H_%M")
        self.file = open("json/%s/%s" % (spider.name, filename), 'wb')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        assert isinstance(item, JournalArticle)
        self.exporter.export_item(item)
        return item