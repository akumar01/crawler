from scrapy.crawler import Crawler
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from agg.spiders.nature_spider import NatureSpider
import os
from ui.custom_crawler import CustomCrawler
import threading
from subprocess import Popen
import subprocess
def do_crawl():

	#spider = NatureSpider()
	#settings = Settings()
	#settings.setmodule('crawler.agg.settings', priority='project')
	#settings.set('SPIDER_MODULES', 'crawler.agg.spiders', priority='project')
	#print settings.getdict('ITEM_PIPELINES')
	#crawler = Crawler(spider, settings)
	#crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
	#crawler.crawl()

	#reactor.run()
	#process = CrawlerProcess(settings)
	#process.crawl(spider)
	#process.start()

	#settings.set('SPIDER_MODULES', 'crawler.agg.spiders', priority='project')
	#pdb.set_trace()
	#process = CustomCrawler(settings)
	#process.crawl(spider)
	#process.start(stop_after_crawl=True)
	#        crawler = Crawler(spider, settings)
	#        crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
	#        crawler.crawl()
	#runner = CrawlerRunner(settings)
	#d = runner.crawl(spider)
	#d.addBoth(lambda _: reactor.stop())
	#reactor.run()

	# Subprocess

	script = ["scrapy", "crawl", "nature_news"]

	try:
		p = Popen(script, cwd = '%s/crawler/agg' % os.getcwd())
		p.wait()
		print('Crawl Finished!')
	except subprocess.CalledProcessError:
		pass
	except OSError:
		pass
if __name__ == "__main__":
    do_crawl()