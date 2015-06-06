# -*- coding: utf-8 -*-

# Scrapy settings for eventpage project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'eventpage'

SPIDER_MODULES = ['eventpage.spiders']
NEWSPIDER_MODULE = 'eventpage.spiders'

ITEM_PIPELINES = {
    'eventpage.pipelines.EventpagePipeline': 100,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'eventpage (+http://www.yourdomain.com)'
