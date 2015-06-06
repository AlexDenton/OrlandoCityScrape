__author__ = 'alex.denton'

import scrapy
from eventlist.items import EventlistItem

class EventListSpider(scrapy.Spider):
    name = "eventlist"
    allowed_domains = ["downtownorlando.com"]
    start_urls = [
        "http://www.downtownorlando.com/future/events/?2015-06#.VXMVgc9VhBe",
    ]

    def parse(self, response):
        results = response.xpath('//*[@id="content_right"]/div/div[@class="row-fluid"]')
        item = EventlistItem()
        item['link'] = []

        for r in results:
            test = r.xpath('//*[@class="event_title"]/a/@href')
            item['link'].append(test.extract())
            print(test.extract())

        yield item