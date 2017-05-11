import scrapy
import datetime
import pdb
from lxml import etree
from io import StringIO
from ..items import JournalArticle, JournalArticleHTML

class WashPostSpider(scrapy.Spider):
	name = 'washpost'

	def __init__(self, *args, **kwargs):
		try:
			self.sync_length = int(kwargs['sync_length'])
		except:
			# Volume of article generated is so great that
			# we only sync back to 2 days by default. Currently
			# disabled search for older articles anyways (see below)
			self.sync_length = 2

		# Make article dates an attribute so that it can be modified in
		# the retrieve article method
		self.article_dates = []

	def start_requests(self):
		# Place which sections to grab here. Currently Politics and World
		urls = {
			'Politics': 'https://www.washingtonpost.com/politics/?nid=top_nav_politics',
			'World': 'https://www.washingtonpost.com/world/?nid=menu_nav_world'
		}

		for section, url in urls.iteritems():
			yield scrapy.Request(url=url, callback = self.parse, meta = {'section' : section})

	def parse(self, response):

		articles =	response.css('section.main-content').css('div.story-headline')

		
		for article in articles:
			# If the article is actually a link to a video, ignore it:
			full_class = article.xpath('@class')

			news_article = JournalArticleHTML()
			news_article["spider"] = self.name
			news_article["tags"] = response.meta["section"]
			news_article["date_created"] = datetime.datetime.utcnow().ctime()

			news_article["title"] = article.css('h3').css('a::text').extract_first()
			# Full url is already included
			news_article["html_src"] = article.css('h3').css('a::attr(href)').extract_first()

			# Set file_urls to blank:
			news_article["file_urls"] = []

			# Unlike the usual structure, we have to parse the article html first before we decide to 
			# discard it if it is too old 
			if news_article["html_src"]:
				yield scrapy.Request(url = news_article["html_src"], callback = self.retrieve_article,
												meta = {'item': news_article})
			else:
				continue
		
		''' Given how many articles Washington Post generates, decided that going back
		to retrive more isn't worth it.
		if min(self.article_dates) > datetime.datetime.utcnow()\
								- datetime.timedelta(self.sync_length):
			link = response.urljoin(self.get_older_url(response, article_date))
			pdb.set_trace()
			yield scrapy.Request(url = link, callback = self.parse, 
								 meta = {'pageno':response.meta['pageno'] + 1})
		'''
	
	# Callback to rertrieve the actual article. Current approach is to just grab the 
	# html of the article body, try to parse it to make online assets addressable, and then 
	# pass it along. Later in the pipeline, we use pdfkit to convert the html to a pdf
	def retrieve_article(self, response):

		item = response.meta["item"]

		# Get the article date and decide if we want to continue:
#		article_date = response.xpath('//span[@itemprop=datePublished]')
		article_date = response.css('span.pb-timestamp::attr(content)').extract_first()
		try:
			article_date = article_date.split('T', 1)[0]
		except:
			pdb.set_trace()

		article_datetime = datetime.datetime.strptime(article_date, '%Y-%m-%d')

		# If the article is older than the time we have requested, return None
		if article_datetime < datetime.datetime.utcnow()\
							 - datetime.timedelta(self.sync_length):
			# Set article_html to blank so that it is dropped in the pipeline
			item["article_html"] = []
			return item 

		self.article_dates.append(article_datetime)

		item["date"] = article_date

		# Get the author
		item["authors"] = \
					response.xpath('//span[@itemprop="author"]').xpath('//span[@itemprop="name"]//text()').extract_first()

		# Retrieve the html of the article body. Subsequently we will convert it to a pdf:
		article_body = response.xpath('//article[@itemprop="articleBody"]').extract_first()


		# Parse the article body and prepend the full url to any sources or hrefs
		# Have to use lxml's HTML parser so that we can ignore errors associated with
		# "broken" HTML
		html_parser = etree.HTMLParser()
		html_tree = etree.parse(StringIO(article_body), html_parser)

		links = html_tree.findall('//*[@src]')
		links +=html_tree.findall('//a[@href]')
		base_url = 'https://www.washingtonpost.com'		
		for link in links:
			attr = 'src' if 'src' in link.keys() else 'href'
			url = link.get(attr)
			# There are a few known cases. If the URL starts with \\,
			# then we must prepend https:\\
			# If it only starts with a single backslash, then it is
			# necessary to prepend the physics.aps
			if(url.startswith(r'//')):
				url = 'https:' + url				
			elif(url.startswith(r'/')):
				url = base_url + url

			link.set(attr, url)

		root = etree.tostring(html_tree.getroot(), pretty_print=True, method="html")

		item["article_html"] = root

		return item


	def get_older_url(self, response, article_date):
		# Getting more stories requires that we send the same request that the 
		# "Load more" button seems to do. The response should then be the html 
		# of the additional stories. 

		# Construct the request string
#		pdb.set_trace()
#		request = 'https:'
#		request += response.xpath('//div[@class="button pb-loadmore clear"]//@data-path')
#		request += '?id='
#		request += response.xpath('//div[@="button pb-loadmore clear"]//@')
#		request += '&contentUri=%2F'
#		request += 
		pass
#		return request