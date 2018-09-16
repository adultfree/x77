# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TopicItem(scrapy.Item):
    topic = scrapy.Field()
    link = scrapy.Field()


class TopicContentItem(scrapy.Item):
    image_urls = scrapy.Field()
    filename = scrapy.Field()
    dirname = scrapy.Field()
    context = scrapy.Field()
    torrents = scrapy.Field()
