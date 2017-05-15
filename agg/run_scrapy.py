from scrapy import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys

# Run scrapy programmatically. When calling scrapy from a subprocess
# it is necessary to use the right virtualenv. This is done by calling
# the python interpreted of the scrapy_env followed by this script
# You must 
if __name__ == "__main__":
	spider_name = sys.argv[1]
	process = CrawlerProcess(get_project_settings())
	process.crawl(spider_name)
	process.start()