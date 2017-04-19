import scrapy 
import datetime
import pdb
from ..items import JournalArticle, JournalArticleHTML

class ScienceNewsSpider(scrapy.Spider):
	name = 'science_news'

	def __init__(self, *args, **kwargs):
		try:
			self.sync_length = int(kwargs['sync_length'])
		except Exception as e:
			self.sync_length = 10

	def start_requests(self):
		urls = ['http://www.sciencemag.org/news/latest-news']

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)


	def parse(self, response):
		# Strongly mimic the structure of aps_news because the page is
		# formatted similarly

		pdb.set_trace()

		# Keep track of article dates so we know whether or not we have 
		# to go further back in time

		article_dates = []

		# Direct parsing of the HTML is easy enough:
		articles = response.css('ul.headline-list').css('article.media')
		
		for article in articles:
			news_article = JournalArticleHTML()
			news_article["spider"] = self.name
			news_article["date_created"] = datetime.datetime.utcnow().ctime()

			news_article = parse_science_article(article, news_article)



			article_date = datetime.datetime.strptime(article["date"], '%Y-%m-%d')
			article_dates.append(article_date)
			if article_date < datetime.datetime.utcnow()\
							 - datetime.timedelta(self.sync_length):
				continue
			else:

				# We need to follow the link to the actual article and retrieve and 
				# parse its contents
#				scrapy.Request(url = link, callback = )
				if news_article["html_src"]:
					news_article["html_src"] = response.urljoin(news_article["html_src"])
					yield scrapy.Request(url = news_article["html_src"], 
										callback = self.retrieve_article, meta = {"item":news_article})
				else:
					continue
#				yield news_article

		if min(article_dates) > datetime.datetime.utcnow()\
								- datetime.timedelta(self.sync_length):
			link = response.urljoin(self.get_older_url(response, article_date))
			pdb.set_trace()
			yield scrapy.Request(url = link, callback = self.parse, 
								 meta = {'pageno':response.meta['pageno'] + 1})

	def parse_science_article(self, article, news_article):
		# Get the title
		title = article.css('h2.media__headline').css('a::text').extract_first()
		# Clean up the title, since it is weirdly formatted on science:
		# Remove the new line character at the beginning:
		title = title[2:]
		# Remove leading and trailing spaces
		title.strip()

		news_article["title"] = title

		# Get the authors
		news_article["authors"] = article.css('p.byline').css('a::text').extract_first()

		# Get the article date
		date = article.css('time::text').extract_first()
		# Remove period from the month contraction:
		date2 = date.split()
		date2[0] = date2[0][-1]
		date = date2[0] + ' ' date2[1] + ' ' date2[2]
		news_article["date"] = date

		# Get the 