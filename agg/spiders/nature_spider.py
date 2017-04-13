import scrapy
import datetime
import pdb
from ..items import JournalArticle

class NatureSpider(scrapy.Spider):
	name = "nature_news"

	def start_requests(self):
		urls = [
			'http://www.nature.com/nature/archive/category.html?code=archive_news_views'
		]
		for url in urls:
			yield scrapy.Request(url=url, callback = self.parse)

	def parse(self, response):
		page = response.url.split("/")[-2]
		filename = 'nature_news-%s.html' % page

		# For each article, find its content tags, article description, and download full PDF
		for article in response.css('article'):
			a_tags = article.css('a::text').extract()
			# If link to PDF isn't available, we aren't interested:
			try:
				PDF_ind = a_tags.index(u'PDF')
			except:
				continue

			news_article = JournalArticle()
			# Some pipeline methods do not take the spider as an argument, but nonetheless
			# need to identify which spider created the item for organizational purposes
			news_article["spider"] = self.name
			news_article["title"] = a_tags[0]
			news_article["authors"] = article.css("ul.authors").css("li::text").extract()
			news_article["tags"] = a_tags[PDF_ind + 1]
			pdf_url = article.css('a::attr(href)')[PDF_ind].extract()
			news_article["file_urls"] = ["http://www.nature.com" +\
									article.css('a::attr(href)')[PDF_ind].extract()]
			news_article["date_created"] = datetime.datetime.utcnow().ctime()
			# Continue to follow links backwards in time to the date specified
			# current_date = 


#			news_article["pdf_url"] = 
#			yield {
#				'title' : a_tags[0],
#				'author' : article.css("ul.authors").css("li::text").extract(),
#				'tags' : a_tags[PDF_ind + 1:],
#				'file_urls' : 
#			}
			yield news_article
