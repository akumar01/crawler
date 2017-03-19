import scrapy

class JournalArticle(scrapy.Item):
	title = scrapy.Field()
	authors = scrapy.Field()
	tags = scrapy.Field()
	pdf_url = scrapy.Field()
