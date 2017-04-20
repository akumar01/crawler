# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import os
import hashlib
import pdb
import datetime
import scrapy
import logging
import pdfkit
from scrapy.pipelines.files import FilesPipeline
from scrapy.exporters import JsonLinesItemExporter
from agg.items import JournalArticle, JournalArticleHTML
from scrapy.exceptions import DropItem

class AggPipeline(object):
    def process_item(self, item, spider):

        # Need to do special processing for sources that do not directly
        # yield PDFs
        if spider.name in ['aps_news', 'science_news']:
            item = self.html_to_pdf(item, spider)
            item = self.standardize(item, spider)
        elif spider.name in ["nature_news"]:
            # Move downloaded files to appropriate directory and rename them:
            item = self.move_files(item, spider)

        # Strip item fields of leading and trailing blank space:
        item = self.clean_spaces(item, spider)
        return item
        

    def clean_spaces(self, item, spider):
        # use isinstance(..., basestring) to check if the value is a string
        for key in item.keys():
            if(isinstance(item[key], basestring)):
                item[key] = item[key].strip()


        # Make sure if any of title, tags,
        # or author is empty, set it to a blank string
        if(not item["title"]):
            item["title"] = ""
        if(not item["authors"]):
            item["authors"] = ""
        if(not item["tags"]):
            item["tags"] = ""

        return item 

    def move_files(self, item, spider):
        # First, make sure that the directory we wish to move the files to exists. 
        # If not, we have to create it

        f = 0;
        for file in item["files"]:
            filename = file["path"].split("/")[1]

            self.create_dirs(spider.name)

            if(not os.path.exists('files/%s/%s' % (spider.name, filename))):
                os.rename("files/%s" % file["path"], "files/%s/%s" %\
                                (spider.name, filename))
            # Set the item file path to the new location and name
            item["files"][f]["path"] = "%s/%s" % (spider.name, filename)
            # f+=1
        return item

    # Check if the desired directory structure exists, and if not, create
    # it. 
    def create_dirs(self, name):
        if(not os.path.exists("files")):
            os.makedirs("files")
        if(not os.path.exists("files/%s" % name)):
            os.makedirs('files/%s' % name)

    def standardize(self, item, spider):
        # Convert the item to standard JournalArticle format 
        if(type(item) != JournalArticle):
            try:
                standard_item = JournalArticle()
                for key in item.keys():
                    if key != "files" and key in standard_item.fields:
                        standard_item[key] = item[key]
                standard_item["files"] = [{}]
                # Can't generate our own checksums at the moment
                standard_item["files"][0]["checksum"] = []
                standard_item["files"][0]["url"] = item["html_src"]
                standard_item["files"][0]["path"] = item["files"] 
                item = standard_item
            except:
                raise DropItem('item could not be standardized')

        return item               

    def html_to_pdf(self, item, spider):
    # Use pdfkit to convert the html file to a pdf file.
    # Need a good way to generate a filename

        if item["html_src"] and item["article_html"]:
            filename = hashlib.sha1(item["html_src"]).hexdigest()
            filename_full = '%s/' % spider.name + filename + '.pdf'
            self.create_dirs(spider.name)

            if(not os.path.exists('files/%s' % filename_full)):
                pdfkit.from_string(item["article_html"], 'files/%s' % filename_full)
                item["files"] = filename_full
            else:
                logging.log(logging.INFO, "File already exists!")
                raise DropItem("No file contained, possible duplicate")
            return item

        else:
            raise DropItem("No html source was found")


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

    def item_completed(self, results, item, info):
        for result in results:
            if results[0]:
                if not result[1]['path']:
                    raise DropItem('No file contained, possible duplicate')
            else:
                raise DropItem('Item failed to download')

        item = super(DownloadPDFS, self).item_completed(results, item, info)

        return item

    # def get_media_requests(self, item, info):
    #     # use 'accession' as name for the image when it's downloaded
    #     return [scrapy.Request(x, meta={'file_folder': item["spider"]})
    #             for x in item.get('file_urls', [])]

    # # write in current folder using the name we chose before
    # def file_path(self, request, response=None, info=None):
    #     media_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
    #     media_ext = os.path.splitext(url)[1]  # change to request.url after deprecation
    #     return 'full/%s/%s%s' % (media_guid, request.meta['file_folder'], media_ext)


# Used for exporting items to json
class JsonPipeline(object):

    def open_spider(self, spider):
        # Initialize the directories where the jsonlines file for the spider
        # is to be saved
        if(not os.path.exists('json_out')):
            os.makedirs('json_out')

        self.file = open('json_out/%s.json' % spider.name, 'ab')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    # def open_spider(self, spider):

    #     # Initialize the directories where the jsonlines file is to be saved:
    #     if(not os.path.exists("json")):
    #         os.makedirs("json")

    #     if(not os.path.exists("json/%s" % spider.name)):
    #         os.makedirs("json/%s" % spider.name)

    #     # Make the JSONlines filename the datetime up to the minute
    #     filename = datetime.datetime.utcnow().strftime("%y_%b_%d_%H_%M")
    #     self.file = open("json/%s/%s" % (spider.name, filename), 'wb')
    #     self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
    #     self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        assert isinstance(item, JournalArticle)
        # This is kind of a hack to deal with instances where
        # the file was likely unable to be downlaoded
        try:
            if(item["files"]):
                self.exporter.export_item(item)
        except:
            pass
        return item