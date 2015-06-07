# -*- coding: utf-8 -*-
import scrapy

from icalendar import Calendar
from eventpage.items import EventpageItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.signalmanager import SignalManager
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import copy
import sys
import pytz

class EventSpider(CrawlSpider):

    cal = Calendar()
    name = "eventpage"
    allowed_domains = ["downtownorlando.com"]
    start_urls = [
        'http://www.downtownorlando.com/future/events/?2015-07'
    ]
    rules = (
        Rule(LinkExtractor(allow=('/events/', ), restrict_xpaths=('//li[@class="event_title"]')), callback='parse_item'),
    )

    def __init__(self, *args, **kwargs):
        super(EventSpider, self).__init__(*args, **kwargs)
        SignalManager(dispatcher.Any).connect(
            self.closed_handler, signal=signals.spider_closed)

        self.cal['PRODID'] = "CFORLANDO"
        self.cal['VERSION'] = "2.0"

    def parse_item(self, response):
        item = EventpageItem()
        item['url'] = response.url
        item['date'] = []
        item['content'] = []

        for ul in response.xpath('//ul'):
            # Grab the two date lines
            for sel in ul.xpath('li[@class="date"]/span[@class="span9"]/text()').extract():
                item['date'].append(sel.strip())

            # Grab the location
            location = ul.xpath('li[@class="location"]/span[@class="span9"]/text()').extract()
            for sel in location:
                item['location'] = sel.strip()
                break

        for sel in response.xpath('//h1[@class="event_title"]/text()').extract():
            item['title'] = sel.strip()
            break

        for sel in response.xpath('//div[@class="event_about"]/p/text()').extract():
            item['content'].append(sel.strip())

        yield item

    def closed_handler(self, spider):
        if spider is not self:
            return

        with open('events_cal.ics', 'wb') as f:
            f.write(self.cal.to_ical())
