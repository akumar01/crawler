import scrapy 
import datetime
import pdb
from lxml import etree
from io import StringIO
from ..items import JournalArticle, JournalArticleHTML

class ScienceNewsSpider(scrapy.Spider):
	name = 'science_news'

	def __init__(self, *args, **kwargs):
		try:
			self.sync_length = int(kwargs['sync_length'])
		except Exception as e:
			self.sync_length = 10
		self.base_url = 'https://www.sciencemag.org'

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

			# The date format is particular to the source
			# Consult the bottom of the datetime module documentation 
			article_date = datetime.datetime.strptime(article["date"], '%b %d, %Y')
			article_dates.append(article_date)

			# If the article is older than the time period we are interested in, 
			# ignore it. 

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
					news_article["html_src"] = self.base_url + news_article["html_src"]
					yield scrapy.Request(url = news_article["html_src"], 
										callback = self.retrieve_article, meta = {"item":news_article})
				else:
					continue
#				yield news_article

		if min(article_dates) > datetime.datetime.utcnow()\
								- datetime.timedelta(self.sync_length):
			link = self.base_url + self.get_older_url(response)
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

		# Science does not put leading zeros on their days. Fix this:
		date_split = date.split()

		date_split[1] = '%02d' % int(date_split[1][:-1])

		# Also get rid of the period at the end of the month
		date = date_split[0][:-1] + ' ' + date_split[1] + ' ' + date_split[2]

		news_article["date"] = date

		# tags are retrieved from the article itself
		
		# This is a relative url that needs to be modified subsequently
		news_article["html_src"] = article.css('h2.media_headline').css('a::attr(href)').extract_first()

		return news_article

	def retrieve_article(self, response):
		# Retrieve the html of the article body. Subsequently we will convert it to a pdf:
		# We need to parse this body and replace relative links with their full forms
		item = response.meta["item"]
		article_body = response.css('div.article__body').extract_first()

		html_parser = etree.HTMLParser()
		html_tree = etree.parse(StringIO(article_body), html_parser)

		links = html_tree.findall('//a[@href]')
		link += html_tree.findall('//*[@src]')
		for link in links:
			attr = 'src' if 'src'in link.keys() else 'href'
			url = link.get(attr)
			# Currently only aware of relative links to within the sciencemag domain. 
			if(url.startswith(r'/')):
				url = self.base_url + url

			link.set(attr, url)

		item["article_html"] = etree.tostring(html_tree.getroot(), pretty_print = True, method='html')

		return item

	def get_older_url(self, response):
		# Science conveniently has a next page button that we can find regardless
		# of the current page
		return response.xpath("//a[@title='Go to next page']").css('a::attr(href)').extract_first()
