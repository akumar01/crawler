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
			# we only sync back to 1 day by default
			self.sync_length = 1

	def start_requests(self):
		# Place which sections to grab here. Currently Politics and World
		urls = {
			'Politics': 'https://www.washingtonpost.com/politics/?nid=top_nav_politics',
			'World': 'https://www.washingtonpost.com/world/?nid=menu_nav_world'
		}

		for section, url in urls.iteritems():
			yield scrapy.Request(url=url, callback = self.parse, meta = {'section' : section})

	def parse(self, response):

		# Keep track of article dates so we can determine whether we must navigate to
		# the next page to get older articles

		articles =	response.css('section.main-content').css('div.story-headline')

		
		for article in articles:
			news_article = JournalArticleHTML()
			news_article["spider"] = self.name
			news_article["tags"] = response.meta["section"]
			news_article["date_created"] = datetime.datetime.utcnow().ctime()

			news_article["title"] = article.css('h3').css('a::text').extract_first()
			# Full url is already included
			news_article["html_src"] = article.css('h3').css('a::attr(href)').extract_first()

			# Unlike the usual structure, we have to parse the article html first before we decide to 
			# discard it if it is too old 
			if news_article["html_src"]:
				news_article = scrapy.Request(url = news_article["html_src"], callback = self.retrieve_article)

				if not news_article:
					continue
				else:
					yield news_article
			else:
				continue


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
		
	
	# Callback to rertrieve the actual article. Current approach is to just grab the 
	# html of the article body, try to parse it to make online assets addressable, and then 
	# pass it along. Later in the pipeline, we use pdfkit to convert the html to a pdf
	def retrieve_article(self, response):

		# Get the article date and decide if we want to continue:
		article_date = response.xpath('//span[@itemprop=datePublished]')
		pdb.set_trace()


		# Retrieve the html of the article body. Subsequently we will convert it to a pdf:
		item = response.meta["item"]
		article_body = response.css('article.main-content').extract_first()
		# Parse the article body and prepend the full url to any sources or hrefs
		# Have to use lxml's HTML parser so that we can ignore errors associated with
		# "broken" HTML
		html_parser = etree.HTMLParser()
		html_tree = etree.parse(StringIO(article_body), html_parser)

		links = html_tree.findall('//*[@src]')
		links +=html_tree.findall('//a[@href]')
		base_url = 'https://physics.aps.org'		
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
		# Currently, we use the kludge solution of explicitly navigating to the
		# url of the next page. Currently do not have a better way to do this.
		return '?page=%d' % (response.meta['pageno'] + 1)