# -*- coding: utf-8 -*-
import scrapy

from eventpage.items import EventpageItem

class EventSpider(scrapy.Spider):
    name = "eventpage"
    allowed_domains = ["downtownorlando.com"]
    start_urls = (
        'http://www.downtownorlando.com/events/war-drugs/#.VXMYflxViko',
    )

    def parse(self, response):
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
