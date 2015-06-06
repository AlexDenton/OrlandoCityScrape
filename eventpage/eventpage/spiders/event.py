# -*- coding: utf-8 -*-
import scrapy

from eventpage.items import EventpageItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class EventSpider(CrawlSpider):
    name = "eventpage"
    allowed_domains = ["downtownorlando.com"]
    start_urls = [
        'http://www.downtownorlando.com/future/events/?2015-06'
    ]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('/events/', ), restrict_xpaths=('//li[@class="event_title"]')), callback='parse_item'),
    )

    # def parse_item(self, response):
    #     self.log('Hi, this is an item page! %s' % response.url)
    #     item = scrapy.Item()
    #     item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
    #     item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
    #     item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
    #     return item

    def parse_item(self, response):
        item = EventpageItem()
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
