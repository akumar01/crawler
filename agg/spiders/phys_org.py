import scrapy
import datetime
import pdb
from lxml import etree
from io import StringIO
from ..items import JournalArticle, JournalArticleHTML

class WashPostSpider(scrapy.Spider):
	name = 'phys_org'

	def __init__(self, *args, **kwargs):
		try:
			self.sync_length = int(kwargs['sync_length'])
		except:
			# Volume of article generated is so great that
			# we only sync back to 2 days by default.
			self.sync_length = 15

		# Make article dates an attribute so that it can be modified in
		# the retrieve article method
		self.article_dates = []

	def start_requests(self):
		# Place which sections to grab here. Currently Condensed Matter and 
		urls = {
			'Condensed Matter' : 'https://phys.org/physics-news/materials/sort/date/all/',
			'Quantum Physics': 'https://phys.org/physics-news/quantum-physics/sort/date/all/',
			'Superconductivity': 'https://phys.org/physics-news/superconductivity/sort/date/all/',
			'Nanophysics': 'https://phys.org/nanotech-news/nano-physics/sort/date/all/'
		}

		for section, url in urls.iteritems():
			yield scrapy.Request(url=url, callback = self.parse, meta = {'section' : section,
																		 'pageno' : 1})

	def parse(self, response):

		articles =	response.xpath('//*[@id="container"]/section/section/section/section/div/article')

		for article in articles:
			# Phys.org articles require us to navigate to a separate page to fully retrieve the
			# article, but once we do this there is conveniently a PDF page to download
			news_article = JournalArticle()
			news_article["spider"] = self.name
			news_article["tags"] = response.meta["section"]
			news_article["date_created"] = datetime.datetime.utcnow().ctime()

			news_article["title"] = article.css('h3').css('a::text').extract_first()
			try:
				news_article["date"] = article.xpath('div/div/text()')[1].extract()\
																		.split('\n')[0]
			except:
				pdb.set_trace()
			article_datetime = datetime.datetime.strptime(\
												news_article["date"], '%b %d, %Y')

			self.article_dates.append(article_datetime)

			# If the article is too old, move on
			if  article_datetime < datetime.datetime.utcnow() - \
								   datetime.timedelta(self.sync_length):
				continue

			article_html = article.css('h3').css('a::attr(href)').extract_first()
			# Pursue the pdf link from the article page itself
			yield scrapy.Request(url = article_html, callback = self.retrieve_article,
								 meta = {'item': news_article})
		

		# Determine if we have to go on to the next page to grab older articles, 
		# and if so, do it:
		if min(self.article_dates) > datetime.datetime.utcnow()\
								- datetime.timedelta(self.sync_length):
			link = response.urljoin(self.get_older_url(response.meta['pageno'] + 1))
			yield scrapy.Request(url = link, callback = self.parse, 
								 meta = {'pageno':response.meta['pageno'] + 1})
	
	# Grab the pdf link and authors only (Phys.org makes it easy)
	def retrieve_article(self, response):

		item = response.meta["item"]
		item["authors"] = response.xpath('//header[@class="content-head"]/h5/text()')\
									.extract_first().split('by ')[1].split('\n')[0]
		item["file_urls"] = response.xpath('//a[@title="Save as pdf file"]/@href').extract()
		return item


	def get_older_url(self, page_number):
	# For phys.org, it is easy if we keep track of the pagenumbers
		return 'page%d' % page_number