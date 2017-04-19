# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JournalArticle(scrapy.Item):
	spider = scrapy.Field()
	title = scrapy.Field()
	authors = scrapy.Field()
	tags = scrapy.Field()
	file_urls = scrapy.Field()
	files = scrapy.Field()
	source_name = scrapy.Field()
	date_created = scrapy.Field()
	date = scrapy.Field()

class JournalArticleHTML(JournalArticle):
	article_html = scrapy.Field()
	html_src = scrapy.Field()