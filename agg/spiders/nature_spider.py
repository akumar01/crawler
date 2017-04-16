import scrapy
import datetime
import pdb
from ..items import JournalArticle

class NatureSpider(scrapy.Spider):
	name = "nature_news"

	def __init__(self, *args, **kwargs):
		self.sync_length = int(kwargs['sync_length'])

	def start_requests(self):
		urls = [
			'http://www.nature.com/nature/archive/category.html?code=archive_news_views'
		]
		for url in urls:
			yield scrapy.Request(url=url, callback = self.parse)

	def parse(self, response):
		page = response.url.split("/")[-2]
		filename = 'nature_news-%s.html' % page

		# Keep track of the article dates so that we can determine 
		# whether we must navigate to the next page to get older articles
		article_dates = []
		for article in response.css('article'):

			a_tags = article.css('a::text').extract()
			# If link to PDF isn't available, we aren't interested:
			try:
				PDF_ind = a_tags.index(u'PDF')
			except:
				continue

			news_article = JournalArticle()


			news_article["date"] = article.css("span.time::text").extract_first()
			# Format the article date into a datetime object. %d is day of the month with
			# leading zeros. %B is full month name, and %y is full year. Keep note if Nature 
			# changes their formatting standard. For example, Nature uses leading zeroes.
			article_date = datetime.datetime.strptime(news_article["date"], "%d %B %Y")
			article_dates.append(article_date)
			# If the article is older than the timeline over which we are interested, then 
			# stop further processing:
			if article_date < datetime.datetime.utcnow()\
									- datetime.timedelta(self.sync_length):
				continue			

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
			

			yield news_article

		# If the oldest article date is newer than the date requested we sync back to, 
		# then get the link to the next oldest month and continue crawling:
		if min(article_dates) > datetime.datetime.utcnow()\
					- datetime.timedelta(self.sync_length):
			link = response.urljoin(self.get_older_url(response, article_date))
			pdb.set_trace()
			yield scrapy.Request(url = link, callback=self.parse)



	# Given a page html and date, find the link to the next oldest month
	def get_older_url(self, response, article_date):
		# Datetime object for a month in the past
		target_date = article_date - datetime.timedelta(30)

		links_all = response.css('dd')

		if target_date.year != article_date.year:
			# The link for previous years should be the first element returned
			# Furthermore, we should only aim to go one year into the past, hence
			# we select the [1] element 
			year_entry = links_all[0].css('li')[1]
			year_link = year_entry.css('a::attr(href)').extract_first()

			# Currently, there is no support for syncing into the past farther
			# than one month
			link = year_link
		else:
			# The link for the previous months should be the second element
			# returned. Furthermore, we should only aim to go one month into the
			# past, since we do not support syncing more than one month. The
			# months are in ascending order, so we need to select the second to 
			# last entry.
			month_entry = links_all[1].css('li')[-2]
			link = month_entry.css('a::attr(href)').extract_first()
		return link