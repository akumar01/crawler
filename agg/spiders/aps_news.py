import scrapy
import datetime
import pdb
from lxml import etree
from io import StringIO
from ..items import JournalArticle

class APSNewsSpider(scrapy.Spider):
	name = 'aps_news'

	def __init__(self, *args, **kwargs):
		try:
			self.sync_length = int(kwargs['sync_length'])
		except:
			self.sync_length = 10

	def start_requests(self):
		urls = [
			'https://physics.aps.org/browse'
		]

		for url in urls:
			yield scrapy.Request(url=url, callback = self.parse, meta = {'pageno' : 1})

	def parse(self, response):

		# Keep track of article dates so we can determine whether we must navigate to
		# the next page to get older articles


		# Cannot directly parse the html for this one, instead parse some javascript
		# result at the end of the html body
		article_string = response.css('body').css('script').extract()[-1]
		article_string = article_string.split('window.results', 1)[1]
		article_string = article_string.split(':',1)[1]
		article_string = article_string.split(',"facets":{')[0]
		articles = self.parse_aps(article_string)
	
		article_dates = []
		
		for article in articles:
			news_article = JournalArticle()
			news_article["spider"] = self.name
			news_article["date_created"] = datetime.datetime.utcnow().ctime()
			for field in article.keys():
				news_article[field] = article[field]
			news_article["file_urls"] = [response.urljoin(news_article["file_urls"])]
			article_date = datetime.datetime.strptime(article["date"], '%Y-%m-%d')
			article_dates.append(article_date)
			if article_date < datetime.datetime.utcnow()\
							 - datetime.timedelta(self.sync_length):
				continue
			else:

				# We need to follow the link to the actual article and retrieve and 
				# parse its contents
#				scrapy.Request(url = link, callback = )
				yield scrapy.Request(url = news_article["file_urls"][0], 
										callback = self.retrieve_article, meta = {"item":news_article})
#				yield news_article


		if min(article_dates) > datetime.datetime.utcnow()\
								- datetime.timedelta(self.sync_length):
			link = self.response.urljoin(self.get_older_url(response, article_date))
			pdb.set_trace()
			yield scrapy.Request(url = link, callback = self.parse, 
								 meta = {'pageno':response.meta['pageno'] + 1})
		
	def parse_aps_article(self, article_string):
		# Get the necessary information for an article:
		article = {}

		# Use the same keys as fields in JournalArticle to 
		# allow for easy transfer later on in the pipeline
		
		# In the case that a given field cannot be parsed, 
		# set the field to empty


		try:
			title = article_string.split('"title":"', 1)[1]
			article["title"] = title.split('",', 1)[0]
		except:
			article["title"] = []	

		try:
			# We make a key assumption that here that the link to the article
			# follows the tile entry
			link = title.split('"link":"')[1]
			link = link.split('"')[0]
			# We cannot just download a pdf of this guy, so this will
			# require some post-processing
			article["file_urls"] = link
		except:

			article["file_urls"] = []	

		try:
			authors = article_string.split('"authors":"')[1]
			article["authors"] = authors.split('",', 1)[0]
		except:
			article["authors"] = []

		try:
			subject_area = article_string.split('"subject_areas":[')[1]
			subject_area = subject_area.split('"label":"')[1]
			subject_area = subject_area.split('"', 1)[0]
			article["tags"] = subject_area
		except:
			article["tags"]  = []

		try:
			date = article_string.split('"date":"')[1]
			date = date.split('"', 1)[0]
			article["date"] = date
		except:
			article["data"] = []
			
		return article

	def parse_aps(self, raw_string):
		# The approach to parsing the returned script is to find the locations
		# of the start and end of article listings. We then search these ranges
		# one at a time for the desired information.
		article_start_inds = []
		article_end_inds = []
		bracket_level = 0
		c_ind = 0
		for c in raw_string:
			if c == "{":
				bracket_level += 1
				# A bracket level of 1 means a new article has started,
				# keep track of its index
				if bracket_level == 1:
					article_start_inds.append(c_ind)
			elif c == "}":
				bracket_level -= 1
				# A bracket level of 0 means we have closed all brackets,
				# thereby ending an article. Keep track of this index
				if bracket_level == 0:
					article_end_inds.append(c_ind)
			c_ind += 1

		assert(len(article_start_inds) == len(article_end_inds))

		# Now go back and extract the necessary information from each article section:
		articles = []
		for i in range(len(article_start_inds)):
			articles.append(self.parse_aps_article(raw_string[article_start_inds[i]:
															article_end_inds[i]]))
		return articles

	# Callback to rertrieve the actual article. Current approach is to just grab the 
	# html of the article body, try to parse it to make online assets addressable, and then 
	# pass it along. Later in the pipeline, we use pdfkit to convert the html to a pdf
	def retrieve_article(self, response):
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

		pdb.set_trace()


		item["article_html"] = root
		return item


	def get_older_url(self, response, article_date):
		# Currently, we use the kludge solution of explicitly navigating to the
		# url of the next page. Currently do not have a better way to do this.
		return '?page=%d' % (response.meta['pageno'] + 1)