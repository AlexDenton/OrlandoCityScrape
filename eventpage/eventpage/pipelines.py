# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from icalendar import Calendar, Event
from icalendar.prop import vDate
import uuid
import re
import datetime

import dateutil.parser

class EventpagePipeline(object):

    def process_item(self, item, spider):

        #FIXME parse the time too
        date = dateutil.parser.parse(item['date'][0]).date()

        event = Event()
        event['UID'] = uuid.uuid4()
        event['DTSTAMP'] = vDate(date)
        event['DTSTART'] = vDate(date)
        event['DTEND'] = vDate(datetime.datetime.combine(date, datetime.time(1, 0)))
        event['ORGANIZER'] = re.sub('[^a-zA-Z0-9]+', '-', item['title'])
        event['SUMMARY'] = item['content'][0]
        spider.cal.add_component(event)

# UID:uid1@example.com
# DTSTAMP:19970714T170000Z
# ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
# DTSTART:19970714T170000Z
# DTEND:19970715T035959Z
# SUMMARY:Bastille Day Party

        return item
