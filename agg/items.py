# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JournalArticle(scrapy.Item):
	title = scrapy.Field()
	authors = scrapy.Field()
	tags = scrapy.Field()
	file_urls = scrapy.Field()
	files = scrapy.Field()
	source_name = scrapy.Field()
