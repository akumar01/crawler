# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2

class AggPipeline(object):
    def process_item(self, item, spider):
    	# Download the pdf:
#    	pdf = urllib2.urlopen(item["pdf_url"])
#    	file = open('files/test_pdf.pdf', 'wb')
#    	file.write(pdf.read())
#    	file.close()
#    	print("file written")
        return item