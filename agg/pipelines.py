# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import os

class AggPipeline(object):
    def process_item(self, item, spider):
    	# Move downloaded files to appropriate directory and rename them:
    	self.move_files(item, spider)
    	# Save the item information to a json file
    	self.save_item(item, spider)


    def move_files(self, item, spider):
    	# First, make sure that the directory we wish to move the files to exists. 
    	# If not, we have to create it:
    	f = 0;
    	for file in item["files"]:
    		filename = file["path"].split("/")[1]
	    	if(not os.path.exists("files/%s" % spider.name)):
	    		os.makedirs("files/%s" % spider.name)

	    	if(not os.path.exists('files/%s/%s' % (spider.name, filename))):
		    	os.rename("files/%s" % file["path"], "files/%s/%s" %\
								(spider.name, filename))
	    	# Set the item file path to the new location and name
	    	item["files"][f]["path"] = "%s/%s" % (spider.name, filename)
	    	f+=1
        return item