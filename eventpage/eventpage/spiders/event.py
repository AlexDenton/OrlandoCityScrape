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

    DELTAS = {
        'SECONDLY': timedelta(seconds=1),
        'MINUTELY': timedelta(minutes=1),
        'HOURLY': timedelta(hours=1),
        'WEEKLY': timedelta(weeks=1),
        'MONTHLY': relativedelta(months=1),
    }

    WEEKDAYS = {
        'MO': 0,
        'TU': 1,
        'WE': 2,
        'TH': 3,
        'FR': 4,
        'SA': 5,
        'SU': 6
    }

    cal = Calendar()
    name = "eventpage"
    allowed_domains = ["downtownorlando.com"]
    start_urls = [
        'http://www.downtownorlando.com/future/events/?2015-07'
    ]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('/events/', ), restrict_xpaths=('//li[@class="event_title"]')), callback='parse_item'),
    )
    closed = 'done'

    # def parse_item(self, response):
    #     self.log('Hi, this is an item page! %s' % response.url)
    #     item = scrapy.Item()
    #     item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
    #     item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
    #     item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
    #     return item

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

        # with open('events_cal.csv', 'wb') as w:
        #     timezone = pytz.timezone('America/Los_Angeles')
        #     format = '%Y-%m-%d'
        #     start_date = timezone.localize(
        #         datetime.strptime('1970-01-01', format))
        #     end_date = timezone.localize(
        #         datetime.strptime('3000-01-01', format))
        #
        #     with open('events_cal.ics', 'r') as f:
        #         for line in self.process(f.readline(), start_date, end_date):
        #             w.write(line.encode("utf-8"))

    def process(ics_string, end_date, start_date=None, include_full_day=False):
        cal = Calendar.from_ical(ics_string)

        heading = 'UID,CREATED,LAST-MODIFIED,DTSTART,DTEND,SUMMARY,LOCATION'
        yield heading

        keys = heading.split(',')

        for item in cal.walk():
            if item.name != 'VEVENT':
                continue

            try:
                item_start = item['DTSTART'].dt
                item_end = item['DTEND'].dt
            except KeyError, e:
                sys.stderr.write("KeyError on item: %s\n\t%s\n\n" % (item, e))
                continue

            if (isinstance(item_start, date) and not isinstance(item_start, datetime)
                and not include_full_day):
                continue

            if (start_date is not None and start_date > item_start) or end_date < item_end:
                continue

            item['SUMMARY'] = item['SUMMARY'].replace(',', ';')
            item['LOCATION'] = item['LOCATION'].replace(',', ';')

            yield ','.join(unicode(item[key].dt)
                           if hasattr(item[key], 'dt')
                           else unicode(item[key])
                           for key in keys)

            # Handle recurrence rules
            if 'RRULE' in item:
                rrule = item['RRULE']
                delta = DELTAS[rrule['FREQ'][0]]
                recur_item = {key: copy.copy(item[key].dt)
                              if hasattr(item[key], 'dt')
                              else item[key]
                              for key in keys}

                rooted_deltas = [timedelta(days=0)]
                if 'BYDAY' in rrule:
                    first_day = WEEKDAYS[rrule['BYDAY'][0]]
                    rooted_deltas.extend([timedelta(days=WEEKDAYS[day] - first_day)
                                          for day in rrule['BYDAY'][1:]])

                if 'UNTIL' in rrule:
                    until = rrule['UNTIL'][0]

                    while recur_item['DTSTART'] <= until:
                        recur_item['DTSTART'] += delta
                        recur_item['DTEND'] += delta

                        unrooted_item = copy.copy(recur_item)
                        for rooted_delta in rooted_deltas:
                            unrooted_item['DTSTART'] += rooted_delta
                            unrooted_item['DTEND'] += rooted_delta
                            yield ','.join(unicode(unrooted_item[key])
                                           for key in keys)
                elif 'COUNT' in rrule:
                    for _ in range(rrule['COUNT']):
                        recur_item['DTSTART'] += delta
                        recur_item['DTEND'] += delta

                        unrooted_item = copy.copy(recur_item)
                        for rooted_delta in rooted_deltas:
                            unrooted_item['DTSTART'] += rooted_delta
                            unrooted_item['DTEND'] += rooted_delta
                            yield ','.join(unicode(unrooted_item[key])
                                           for key in keys)