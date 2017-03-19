import scrapy

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

			yield {
				'title' : a_tags[0],
				'author' : article.css("ul.authors").css("li::text").extract(),
				'tags' : a_tags[PDF_ind + 1:],
#				'file_urls' : 
			}

		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log('Saved file %s' % filename)