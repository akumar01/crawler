import scrapy
import datetime
import pdb
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
			yield scrapy.Request(url=url, callback = self.parse)

	def parse(self, response):


		# Keep track of article dates so we can determine whether we must navigate to
		# the next page to get older articles

		article_dates = []
		pdb.set_trace()
