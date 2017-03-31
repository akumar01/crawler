import six
import signal
import logging
import warnings

import sys
from twisted.internet import reactor, defer
from zope.interface.verify import verifyClass, DoesNotImplement

from scrapy.core.engine import ExecutionEngine
from scrapy.resolver import CachingThreadedResolver
from scrapy.interfaces import ISpiderLoader
from scrapy.extension import ExtensionManager
from scrapy.settings import Settings
from scrapy.signalmanager import SignalManager
from scrapy.exceptions import ScrapyDeprecationWarning
from scrapy.utils.ossignal import install_shutdown_handlers, signal_names
from scrapy.utils.misc import load_object
from scrapy.utils.log import LogCounterHandler, configure_logging, log_scrapy_info
from scrapy import signals
from scrapy.crawler import CrawlerRunner
import pdb

class CustomCrawler(CrawlerRunner):
    def __init__(self, settings=None):
        super(CustomCrawler, self).__init__(settings)
        configure_logging(self.settings)
        log_scrapy_info(self.settings)
        pdb.set_trace()
    def start(self, stop_after_crawl=True):
        """
        This method starts a Twisted `reactor`_, adjusts its pool size to
        :setting:`REACTOR_THREADPOOL_MAXSIZE`, and installs a DNS cache based
        on :setting:`DNSCACHE_ENABLED` and :setting:`DNSCACHE_SIZE`.

        If `stop_after_crawl` is True, the reactor will be stopped after all
        crawlers have finished, using :meth:`join`.

        :param boolean stop_after_crawl: stop or not the reactor when all
            crawlers have finished
        """
        if stop_after_crawl:
            d = self.join()
            # Don't start the reactor if the deferreds are already fired
            if d.called:
                return
            d.addBoth(self._stop_reactor)

        reactor.installResolver(self._get_dns_resolver())
        tp = reactor.getThreadPool()
        tp.adjustPoolsize(maxthreads=self.settings.getint('REACTOR_THREADPOOL_MAXSIZE'))
        reactor.addSystemEventTrigger('before', 'shutdown', self.stop)
        reactor.run(installSignalHandlers=False)  # blocking call

    def _get_dns_resolver(self):
        if self.settings.getbool('DNSCACHE_ENABLED'):
            cache_size = self.settings.getint('DNSCACHE_SIZE')
        else:
            cache_size = 0
        return CachingThreadedResolver(
            reactor=reactor,
            cache_size=cache_size,
            timeout=self.settings.getfloat('DNS_TIMEOUT')
        )

    def _stop_reactor(self, _=None):
        try:
            reactor.stop()
        except RuntimeError:  # raised if already stopped or in shutdown stage
            pass

